import os
import tornado.ioloop
import tornado.web
class GetHandler(tornado.web.RequestHandler):
    # def get(self):
    #     response = self.get_arguments("text")
    #     if len(response) == 0:
    #         self.set_status(400)
    #         return self.finish("Invalid text")

        
    #     # self.write({"key":self.get_argument("key")})

    def get(self):
        file_name = "t.txt"
        path_to_file = os.getcwd()+'/audio/'+file_name
        buf_size = 4096
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
        with open(path_to_file, 'r') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)
        self.finish()

def make_app():
    return tornado.web.Application([
        (r"/", GetHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()