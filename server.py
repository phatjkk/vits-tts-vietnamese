import tornado.ioloop
import tornado.web
from validate import validate_query_params
from tts import text_to_speech 
import hashlib
import os
import json
from pydub import AudioSegment  # Ensure this is at the top of your file


# Define a JSON schema for your query parameters
query_param_schema = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "speed": {"type": "string", "maxLength": 9}
    },
    "required": ["text", "speed"]
}

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('web/index.html')

class MyHandler(tornado.web.RequestHandler):
    @validate_query_params(query_param_schema)
    def get(self):
        # Parameters are already validated here
        text:str = self.get_argument('text')
        speed:str = self.get_argument('speed')
        current_url:str = '{}://{}'.format(self.request.protocol,self.request.host)
        result,file_name = handle_tts_request(text,speed)
        result["audio_url"] =  current_url+"/audio/"+file_name
        self.write(result)

    def post(self):
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            texts: list = data.get('texts')
            speed: str = data.get('speed')
            pause: int = data.get('pause', 500)

            if not texts or not isinstance(texts, list) or not speed:
                self.set_status(400)  # Bad Request
                self.write(json.dumps({"error": "Missing 'texts' (array of strings) or 'speed' in request body."}))
                return

            results = []
            audio_files = []  # Keep track of individual audio file paths
            current_url: str = '{}://{}'.format(self.request.protocol, self.request.host)
            for text in texts:
                result, file_name = handle_tts_request(text, speed)
                result["audio_url"] = current_url + "/audio/" + file_name
                results.append(result)
                # Log each generated audio file
                audio_files.append(file_name)  # Track audio file for combining
                print(f"Generated audio file: {file_name}")

            audio_dir = os.getcwd() + "/audio"
            combined_audio_file_name = combine_audio_files(audio_files, audio_dir, pause=pause)

            # Add the combined audio file to the response
            results.append({
                "combined_audio_url": f"{current_url}/audio/{combined_audio_file_name}"
            })

            self.write(json.dumps(results))

        except json.JSONDecodeError:
            self.set_status(400)  # Bad Request
            self.write(json.dumps({"error": "Invalid JSON in request body."}))
        except Exception as e:
            self.set_status(500)  # Internal Server Error
            self.write(json.dumps({"error": str(e)}))

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

def make_app():
    return tornado.web.Application([
        (r'/', HomeHandler),
        (r"/tts", MyHandler),
        (r'/audio/(.*)', tornado.web.StaticFileHandler, {'path': os.getcwd()+"/audio/"}),
        (r'/assets/(.*)', tornado.web.StaticFileHandler, {'path': os.getcwd()+"/assets/"}),
    ])

def handle_tts_request(text,speed):
    text_hash:str = hashlib.sha1((text+speed).encode('utf-8')).hexdigest()
    file_name = text_hash+ ".wav"
    file_path = os.getcwd()+"/audio/"+file_name
    if os.path.isfile(file_path):
        return ({
            "hash":text_hash,
            "speed":speed,
            },file_name)
    else:
        # create new file 
        model_name = "pretrained_vi.onnx"
        audio_path = text_to_speech(text,speed,model_name,text_hash)
        return ({
            "hash":text_hash,
            "speed":speed,
            },file_name)

def combine_audio_files(audio_files: list, output_dir: str, pause: int = 500) -> str:
    combined_audio = None
    hash_object = hashlib.sha1("".join(audio_files).encode('utf-8'))
    combined_audio_file_name = f"{hash_object.hexdigest()}.wav"
    output_file = f"{output_dir}/{combined_audio_file_name}"
    pause = AudioSegment.silent(pause)  # duration is in milliseconds

    if os.path.isfile(output_file):  # Return existing file if already combined
        return combined_audio_file_name

    for audio_path in audio_files:
        audio = AudioSegment.from_file(f"{output_dir}/{audio_path}")

        if combined_audio is None:  # First audio file
            combined_audio = audio
        else:  # Append subsequent audio files
            combined_audio = combined_audio + pause + audio

    # Export the combined audio to the output file
    combined_audio.export(output_file, format="wav")
    return combined_audio_file_name


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()