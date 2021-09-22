#  coding: utf-8 
import socketserver
import os.path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        
        root = "./www"
        method, file, protocol, host = self.parse_request()  # a dictionary that contains the data of the request's start-line
        
        path = root + file  # path of the resource e.g. "./www/base.html"
        response = None
        
        if file.endswith("/"):
            path = path + "index.html" 

        # Determine the respond
        if method != "GET":  # HEAD POST PUT DELETE are not allowed
            response = self.response_405()     
        elif not file.endswith("/") and os.path.isdir(path):
            redirec_path = file + "/"  # redirect if the file/folder exists e.g. /deep -> /deep/
            response = self.response_301(redirec_path, host)
        elif os.path.isfile(path):
            # only the existing file can be read
            mime_type = self.get_mime_type(path)
            if mime_type != "folder":
                body = self.get_file_content(path)
                if body != "error":
                    response = self.response_200(mime_type, body)
                else:
                    response = self.response_404()
            else:
                response = self.response_404()
        else:
                response = self.response_404()

        self.request.sendall(bytearray(response,'utf-8'))


    # site: https://stackoverflow.com/questions/18563664/socketserver-python by sberry on Sep 1st 2013
    def parse_request(self):
        host = None
        # decoded byte object to string object, then split by \r\n
        lines = self.data.decode("utf-8").splitlines()
        # get the method, file, protocol of the request
        # e.g. ['GET / HTTP/1.1', 'Host: 127.0.0.1:8080', 'User-Agent: curl/7.64.1', 'Accept: */*']
        method, file, protocol = lines[0].split()
        # get the host of the request
        for line in lines:
            if "Host:" in line:
                host = "http://"+line.split()[-1]
        return method, file, protocol, host


    # site: https://docs.python.org/3/library/os.path.html#os.path.splitext
    def get_mime_type(self, path):
        root, ext = os.path.splitext(path)
        if ext != "":
            # the last level of the path indicate a valid file
            return "text/" + ext.split(".")[1]
        else:
            # the last level of the path indicate a folder
            return "folder"
            

    def get_file_content(self, path):
        # read file body
        try:
            f = open(path, "r")
        except Exception:
            body = "error"
        else:
            body = f.read()
            f.close()
        finally:
            return body

    # site: https://eclass.srv.ualberta.ca/pluginfile.php/7447795/mod_resource/content/1/05-HTTP-II.pdf by Abram Hindle under Creative Commons Attribution-ShareAlike 4.0 International License
    def response_200(self, mime_type, body):
        return "HTTP/1.1 200 OK\r\nContent-Type: " + mime_type + "\r\n\r\n" + body + "\r\n"

    def response_301(self, redirec_path, host):
        return "HTTP/1.1 301 Moved Permanently\r\nLocation: " + host + redirec_path + "\r\n"

    def response_404(self):
        return "HTTP/1.1 404 Not Found\r\nConnection: close\r\n"

    def response_405(self):
        return "HTTP/1.1 405 Method Not Allowed\r\nConnection: close\r\n"


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
