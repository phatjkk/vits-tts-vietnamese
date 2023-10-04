import tornado.ioloop
import tornado.web
from validate import validate_query_params
from tts import text_to_speech 
import hashlib
import os
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
            "text":text,
            "speed":speed,
            },file_name)
    else:
        # create new file 
        model_name = "pretrained_vi.onnx"
        audio_path = text_to_speech(text,speed,model_name,text_hash)
        return ({
            "hash":text_hash,
            "text":text,
            "speed":speed,
            },file_name)
    
if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()