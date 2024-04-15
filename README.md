# Finetuining VITS Text-to-Speech Model in Vietnamese

We use Piper library to finetuning VITS for TTS tasks with different voice in Vietnamese. 

We also built a Tornado server to deploy TTS model on microservice with Docker. 
The server uses ONNX model type to infer lightweight and excellent performance. 

Video demo: https://youtu.be/1mAhaP26aQE

Read Project Docs: [Paper](https://github.com/phatjkk/vits-tts-vietnamese/blob/main/TTS_VITS_Docs_NguyenThanhPhat.pdf)

<p align="center">
  <img  src="https://raw.githubusercontent.com/phatjkk/vits-tts-vietnamese/main/resources/web_ui.PNG">
</p>

# How to run this project?

### With Docker (***highly recommend***):
On your terminal, type these commands to build a Docker Image:
```
docker build  ./ -f .Dockerfile -t vits-tts-vi:v1.0
```
Then run it with port 5004:
```
docker run -d -p 5004:8888 vits-tts-vi:v1.0
```
While the Docker Image was running, you now make a request to use the TTS task via this API on your browser.
```
http://localhost:5004/?text=Xin chào bạn&speed=normal
```
The result seems like this:
<p align="center">
  <img  src="https://raw.githubusercontent.com/phatjkk/vits-tts-vietnamese/main/resources/demo_api.PNG">
</p>

```json
{
    "hash": "e6bc1768c82ae63ed8ee61ca2349efa4ef9f166e",
    "text": "xin chào bạn",
    "speed": "normal",
    "audio_url": "http://localhost:5004/audio/e6bc1768c82ae63ed8ee61ca2349efa4ef9f166e.wav"
}
```
The speed has 5 options: *normal*, *fast*, *low*, *very_fast*, *very_slow*

Or you can use the Web UI via this URL:
```
http://localhost:5004/
```
The repo of this React Front-end: [vits-tts-webapp](https://github.com/phatjkk/vits-tts-webapp)
<p align="center">
  <img  src="https://raw.githubusercontent.com/phatjkk/vits-tts-vietnamese/main/resources/web_ui.PNG">
</p>

### With normal way:
In the repo folder, type in Terminal:
```
pip install -r requirements.txt
```
Then run the server file:
```
python server.py
```
Now, you can access the TTS API with port 8888:
```
http://localhost:8888/?text=Xin chào bạn&speed=normal
```
The result also seems like this:
```json
{
    "hash": "e6bc1768c82ae63ed8ee61ca2349efa4ef9f166e",
    "text": "xin chào bạn",
    "speed": "normal",
    "audio_url": "http://localhost:5004/audio/e6bc1768c82ae63ed8ee61ca2349efa4ef9f166e.wav"
}
```

# Result
Audio before finetuning voice (unmute to hear):


https://github.com/phatjkk/vits-tts-vietnamese/assets/48487157/2a3f51b0-4d27-43a9-b5de-8925ddcc8a2b


Audio AFTER finetuining voice (unmute to hear):


https://github.com/phatjkk/vits-tts-vietnamese/assets/48487157/e953f2cc-979d-4fa2-96b2-96786345723d


### Evaluation: 
```
### Metrics in test data BEFORE finetuning:
Mean Square Error: (lower is better) 0.044785238588228825
Root Mean Square Error (lower is better): 2.0110066944004297
=============================================
### Metrics in test data AFTER finetuning:
Mean Square Error: (lower is better) 0.043612250527366996
Root Mean Square Error (lower is better): 1.97773962268741
```

In TTS tasks, the output spectrogram for a given text can be represented in many different ways.
So, loss functions like MSE and MAE are just used to encourage the model to minimize the difference between the predicted and target spectrograms.
The right way to Evaluate TTS model is to use MOS(mean opinion scores) BUT it is a subjective scoring system and we need human resources to do it.
Reference: https://huggingface.co/learn/audio-course/chapter6/evaluation

# How do we preprocess data and fine-tuning?

See **train_vits.ipynb** file in the repo or via this Google Colab:

https://colab.research.google.com/drive/1UK6t_AQUw9YJ_RDFvXUJmWMu-oS23XQs?usp=sharing

Author: Nguyen Thanh Phat - aka phatjk
