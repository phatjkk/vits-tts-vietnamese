# !pip install torch==1.11.0
# !pip install onnxruntime==1.15.1
# !pip install piper-phonemize==1.1.0
import json
import math
import time
from pathlib import Path
from enum import Enum
import os
import numpy as np
import onnxruntime
import hashlib
from typing import List
from wavfile import write as write_wav
from piper_phonemize import phonemize_codepoints, phonemize_espeak, tashkeel_run

# import torch


# def to_gpu(x: torch.Tensor) -> torch.Tensor:
#     return x.contiguous().cuda(non_blocking=True)


def audio_float_to_int16(
    audio: np.ndarray, max_wav_value: float = 32767.0
) -> np.ndarray:
    """Normalize audio and convert to int16 range"""
    audio_norm = audio * (max_wav_value / max(0.01, np.max(np.abs(audio))))
    audio_norm = np.clip(audio_norm, -max_wav_value, max_wav_value)
    audio_norm = audio_norm.astype("int16")
    return audio_norm

class PhonemeType(str, Enum):
    ESPEAK = "espeak"
    TEXT = "text"

def phonemize(config, text: str) -> List[List[str]]:
    """Text to phonemes grouped by sentence."""
    if config["phoneme_type"] == PhonemeType.ESPEAK:
        if config["espeak"]["voice"] == "ar":
            # Arabic diacritization
            # https://github.com/mush42/libtashkeel/
            text = tashkeel_run(text)
        return phonemize_espeak(text, config["espeak"]["voice"])
    if config["phoneme_type"] == PhonemeType.TEXT:
        return phonemize_codepoints(text)
    raise ValueError(f'Unexpected phoneme type: {config["phoneme_type"]}')

PAD = "_"  # padding (0)
BOS = "^"  # beginning of sentence
EOS = "$"  # end of sentence


def phonemes_to_ids(config, phonemes: List[str]) -> List[int]:
    """Phonemes to ids."""
    id_map = config["phoneme_id_map"]
    ids: List[int] = list(id_map[BOS])
    for phoneme in phonemes:
        if phoneme not in id_map:
            print("Missing phoneme from id map: %s", phoneme)
            continue
        ids.extend(id_map[phoneme])
        ids.extend(id_map[PAD])
    ids.extend(id_map[EOS])
    return ids

def load_config(model):
    with open(f"{model}.json", "r") as file:
        config = json.load(file)
    return config

def TTS(text:str,modelName:str):
    """Main entry point"""
    sample_rate = 22050
    noise_scale_w = 0.8
    noise_scale = 0.667
    length_scale = 1.0
    output_dir = os.getcwd()+"/audio/"
    sess_options = onnxruntime.SessionOptions()
    model = onnxruntime.InferenceSession(modelName, sess_options=sess_options)
    config = load_config(modelName)

    text = text.strip()
    
    hashText = hashlib.sha1(text.encode('utf-8')).hexdigest()

    phonemes_list = phonemize(config, text)
    phoneme_ids = []
    for phonemes in phonemes_list:
      phoneme_ids.append(phonemes_to_ids(config, phonemes))

    speaker_id = None

    text = np.expand_dims(np.array(phoneme_ids[0], dtype=np.int64), 0)
    text_lengths = np.array([text.shape[1]], dtype=np.int64)
    scales = np.array(
        [noise_scale, length_scale, noise_scale_w],
        dtype=np.float32,
    )
    sid = None

    if speaker_id is not None:
        sid = np.array([speaker_id], dtype=np.int64)

    start_time = time.perf_counter()
    audio = model.run(
        None,
        {
            "input": text,
            "input_lengths": text_lengths,
            "scales": scales,
            "sid": sid,
        },
    )[0].squeeze((0, 1))
    # audio = denoise(audio, bias_spec, 10)
    audio = audio_float_to_int16(audio.squeeze())
    end_time = time.perf_counter()

    audio_duration_sec = audio.shape[-1] / sample_rate
    infer_sec = end_time - start_time
    # real_time_factor = (
    #     infer_sec / audio_duration_sec if audio_duration_sec > 0 else 0.0
    # )
    output_path = output_dir + f"/{hashText}.wav"
    write_wav(str(output_path), sample_rate, audio)
    return output_path


def denoise(
    audio: np.ndarray, bias_spec: np.ndarray, denoiser_strength: float
) -> np.ndarray:
    audio_spec, audio_angles = transform(audio)

    a = bias_spec.shape[-1]
    b = audio_spec.shape[-1]
    repeats = max(1, math.ceil(b / a))
    bias_spec_repeat = np.repeat(bias_spec, repeats, axis=-1)[..., :b]

    audio_spec_denoised = audio_spec - (bias_spec_repeat * denoiser_strength)
    audio_spec_denoised = np.clip(audio_spec_denoised, a_min=0.0, a_max=None)
    audio_denoised = inverse(audio_spec_denoised, audio_angles)

    return audio_denoised


def stft(x, fft_size, hopsamp):
    """Compute and return the STFT of the supplied time domain signal x.
    Args:
        x (1-dim Numpy array): A time domain signal.
        fft_size (int): FFT size. Should be a power of 2, otherwise DFT will be used.
        hopsamp (int):
    Returns:
        The STFT. The rows are the time slices and columns are the frequency bins.
    """
    window = np.hanning(fft_size)
    fft_size = int(fft_size)
    hopsamp = int(hopsamp)
    return np.array(
        [
            np.fft.rfft(window * x[i : i + fft_size])
            for i in range(0, len(x) - fft_size, hopsamp)
        ]
    )


def istft(X, fft_size, hopsamp):
    """Invert a STFT into a time domain signal.
    Args:
        X (2-dim Numpy array): Input spectrogram. The rows are the time slices and columns are the frequency bins.
        fft_size (int):
        hopsamp (int): The hop size, in samples.
    Returns:
        The inverse STFT.
    """
    fft_size = int(fft_size)
    hopsamp = int(hopsamp)
    window = np.hanning(fft_size)
    time_slices = X.shape[0]
    len_samples = int(time_slices * hopsamp + fft_size)
    x = np.zeros(len_samples)
    for n, i in enumerate(range(0, len(x) - fft_size, hopsamp)):
        x[i : i + fft_size] += window * np.real(np.fft.irfft(X[n]))
    return x


def inverse(magnitude, phase):
    recombine_magnitude_phase = np.concatenate(
        [magnitude * np.cos(phase), magnitude * np.sin(phase)], axis=1
    )

    x_org = recombine_magnitude_phase
    n_b, n_f, n_t = x_org.shape  # pylint: disable=unpacking-non-sequence
    x = np.empty([n_b, n_f // 2, n_t], dtype=np.complex64)
    x.real = x_org[:, : n_f // 2]
    x.imag = x_org[:, n_f // 2 :]
    inverse_transform = []
    for y in x:
        y_ = istft(y.T, fft_size=1024, hopsamp=256)
        inverse_transform.append(y_[None, :])

    inverse_transform = np.concatenate(inverse_transform, 0)

    return inverse_transform


def transform(input_data):
    x = input_data
    real_part = []
    imag_part = []
    for y in x:
        y_ = stft(y, fft_size=1024, hopsamp=256).T
        real_part.append(y_.real[None, :, :])  # pylint: disable=unsubscriptable-object
        imag_part.append(y_.imag[None, :, :])  # pylint: disable=unsubscriptable-object
    real_part = np.concatenate(real_part, 0)
    imag_part = np.concatenate(imag_part, 0)

    magnitude = np.sqrt(real_part**2 + imag_part**2)
    phase = np.arctan2(imag_part.data, real_part.data)

    return magnitude, phase

