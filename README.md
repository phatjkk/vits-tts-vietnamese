# Finetuining VITS Text-to-Speech Model in Vietnamese

We use Piper library to finetuning VITS for TTS tasks with different voice in Vietnamese. 

We also build a Tornado server deploy TTS model on microservice with Docker. 
The server use ONNX model type to inference with lightweight and great performance. 


# How to run this project?

### With Docker (***highly recommend***):
On your terminal, type this commands to build Docker Image:
```
docker build  ./ -f .Dockerfile -t vits-tts-vi:v1.0
```
Then run it with port 5004:
```
docker run -d -p 5004:8888 vits-tts-vi:v1.0
```
While the Docker Image runing, now you make request to use TTS task via this API on your browser.
```
http://localhost:5004/?text=Xin chào bạn
```
The result seem like:
<p align="center">
  <img  src="https://raw.githubusercontent.com/phatjkk/vits-tts-vietnamese/main/resources/demo_api.PNG">
</p>

```json
{
    "hash": "5f560869a0498096ddc31f21ea474418d6e2ab80",
    "text": "Xin chào bạn",
    "audio_url": "http://localhost:5004/audio/5f560869a0498096ddc31f21ea474418d6e2ab80.wav"
}
```

### With normal way:
In repo folder, type in Terminal:
```
pip install -r requirements.txt
```
Then run server file:
```
python server.py
```
Now, you can access to the TTS API with port 8888:
```
http://localhost:8888/?text=Xin chào bạn
```
The result also seem like:
```json
{
    "hash": "5f560869a0498096ddc31f21ea474418d6e2ab80",
    "text": "Xin chào bạn",
    "audio_url": "http://localhost:5004/audio/5f560869a0498096ddc31f21ea474418d6e2ab80.wav"
}
```

# Result
Audio before finetuining voice (unmute to hear):


https://github.com/phatjkk/vits-tts-vietnamese/assets/48487157/2a3f51b0-4d27-43a9-b5de-8925ddcc8a2b


Audio AFTER finetuining voice (unmute to hear):


https://github.com/phatjkk/vits-tts-vietnamese/assets/48487157/e953f2cc-979d-4fa2-96b2-96786345723d


### Evaluation: 
In TTS tasks, output spectrogram for a given text can be represented in many different ways.
So, loss function like MSE and MAE just used for encourage the model to minimize the difference between the predicted and target spectrograms.
The right way to Evaluating TTS model is use MOS(mean opinion scores) BUT it is a subjective scoring system and we need human resource to do it.
Reference: https://huggingface.co/learn/audio-course/chapter6/evaluation

# How do we preprocess data and fine-tuining?

See **train_vits.ipynb** file in the repo or via this Google Colab:

https://colab.research.google.com/drive/1UK6t_AQUw9YJ_RDFvXUJmWMu-oS23XQs?usp=sharing

Author: Nguyen Thanh Phat - aka phatjk
