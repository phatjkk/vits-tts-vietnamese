
import os
import tornado.ioloop
import tornado.web
from tts import TTS 
import hashlib
class GetHandler(tornado.web.RequestHandler):
    def get(self):


        response = self.get_arguments("text")
        if len(response) == 0:
            self.set_status(400)
            return self.finish("Invalid text")
        text = self.get_argument("text")
        speed = self.get_arguments("speed")
        speed = speed[0]
        text_hash:str = hashlib.sha1((text+speed).encode('utf-8')).hexdigest()
        file_name = text_hash+ ".wav"
        file_path = os.getcwd()+"/audio/"+file_name
        current_url = '{}://{}'.format(self.request.protocol,self.request.host)
        if os.path.isfile(file_path):
            self.write({
                "hash":text_hash,
                "text":self.get_argument("text"),
                "speed":self.get_argument("speed"),
                "audio_url": current_url+"/audio/"+file_name
                })
        else:
            # create new file 
            modelName = "pretrained_vi.onnx"
            audio_path = TTS(text,speed,modelName,text_hash)
            self.write({
                "hash":text_hash,
                "text":self.get_argument("text"),
                "speed":self.get_argument("speed"),
                "audio_url": current_url+"/audio/"+file_name
                })

def make_app():
    return tornado.web.Application([
        ((r'/'), GetHandler),
        (r'/audio/(.*)', tornado.web.StaticFileHandler, {'path': os.getcwd()+"/audio/"}),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()