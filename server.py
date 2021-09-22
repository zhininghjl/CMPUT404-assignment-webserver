#  coding: utf-8 
import socketserver
from typing import Protocol

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
        self.request.sendall(bytearray("OK",'utf-8'))

        root = "./www" # root+start_line[1],  # path of the resource e.g. "./www/base.html"
        method, path, protocol = self.parse_request()  # a dictionary that contains the data of the request's start-line
        print("start_line_data: ", method, path, protocol)
        
        mime_type = self.get_mime_type(path)
        print("mime_type: %s\n" % mime_type)

    # site: https://stackoverflow.com/questions/18563664/socketserver-python
    def parse_request(self):
        # decoded byte object to string object, then split by \r\n
        # ['GET / HTTP/1.1', 'Host: 127.0.0.1:8080', 'User-Agent: curl/7.64.1', 'Accept: */*']
        lines = self.data.decode("utf-8").splitlines()
        start_line = lines[0].split()
        return start_line[0], start_line[1], start_line[2]

    def get_mime_type(self, path):
        if "/" == path:
            return "root"

        if path.endswith("/"):
            path = path[:-1]  # remove / at the end
        
        if "/" in path:
            p = path.split("/")[-1]
            if "." in p:
                if len(p.split(".")) == 2:
                    return "text/"+p.split(".")[1]
        return "invalid"


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
