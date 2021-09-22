#  coding: utf-8 
import socketserver
from typing import Protocol
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
        
        method, path, protocol = self.parse_request()  # a dictionary that contains the data of the request's start-line
        print("start_line_data: ", method, path, protocol)
        
        mime_type = self.get_mime_type(path)
        print("mime_type: %s\n" % mime_type)

        
        response = None
        if method != "GET":
            response = self.get_respond(405)
        elif mime_type == "invalid":
            response = self.get_respond(404)
        else:
            body = self.get_file_content(path)
            if body != "error":
                response = self.get_respond(200, mime_type, body)

        self.request.sendall(bytearray(response,'utf-8'))


    # site: https://stackoverflow.com/questions/18563664/socketserver-python by sberry on Sep 1st 2013
    def parse_request(self):
        root = "./www"  # path of the resource e.g. "./www/base.html"
        # decoded byte object to string object, then split by \r\n
        lines = self.data.decode("utf-8").splitlines()
        # ['GET / HTTP/1.1', 'Host: 127.0.0.1:8080', 'User-Agent: curl/7.64.1', 'Accept: */*']
        method, path, protocol = lines[0].split()
        if path.endswith("/"):
            path = path + "index.html"
        return method, root+path, protocol


    # site: https://docs.python.org/3/library/os.path.html#os.path.splitext
    def get_mime_type(self, path):
        root, ext = os.path.splitext(path)
        print("root: ",root, "ext: ",ext)
        if ext != "":
            return "text/" + ext.split(".")[1]
        else:
            return "invalid"
            

    def get_file_content(self, path):
        try:
            f = open(path, "r")
        except Exception as e:
            body = "error"
            print("Err: ", e)
        else:
            body = f.read()
            f.close()
        finally:
            return body


    def get_respond(self, status, mime_type=None, body=None):
        if status == 200:
            return "HTTP/1.1 200 OK\r\nContent-Type: " + mime_type + "\r\n\r\n" + body + "\r\n"
        elif status == 301:
            return "HTTP/1.1 301 Moved Permanently\r\n"
        elif status == 404:
            return "HTTP/1.1 404 Not FOUND!\r\nConnection: close\r\n"
        elif status == 405:
            return "HTTP/1.1 405 Method Not Allowed\r\n"


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
