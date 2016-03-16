#!/usr/bin/python

import time
import BaseHTTPServer
import argparse

HOST_NAME = '' # ip address or nothing to 0.0.0.0
PORT_NUMBER = 6093 # set the listening port

RESPONSE_HEAD = 200
RESPONSE_GET  = 200
RESPONSE_BODY = "OK"

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--port", action="store", type=int, help="Listen on port")
    parser.add_argument("--head-response", action="store", type=int, help="Head HTTP Response for requests (default: 200)")
    parser.add_argument("--get-response", action="store", type=int, help="GET HTTP Response for requests (default: 200)")
    parser.add_argument("--body", action="store", help="Body response for GET")

    args = parser.parse_args()
    # print args.body
    
    global PORT_NUMBER
    global RESPONSE_HEAD
    global RESPONSE_GET
    global RESPONSE_BODY

    if args.port!=None: PORT_NUMBER=args.port 
#    print parser.parse_args(['--body'])
    # print args['body']
    # print body


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        global PORT_NUMBER
        s.wfile.write("%s" %PORT_NUMBER)
        # s.wfile.write("XXX")

if __name__ == '__main__':
    #get_args()
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)