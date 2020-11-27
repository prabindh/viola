from http.server import HTTPServer, BaseHTTPRequestHandler

from io import BytesIO
import os
import json
#from pyautogui import press, keyDown, keyUp
import datetime

serve_from = os.path.dirname(os.path.realpath(__file__))
station_status = {}
timeObjects = []
code = 'up'
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def check_time(self, timeObj):
        global timeObjects;
        # Add to timeObjects
        timeObjects.append(timeObj)
        code = 'up'
        if len(timeObjects) == 1:
            return 'up'
        if len(timeObjects) == 2:
            firstTime = timeObjects[0]
            lastTime = timeObjects[-1]
            diff = lastTime - firstTime
            if diff.microseconds >= 800*1000:
                return 'up'
            else:
                return 'left'
        if len(timeObjects) >= 3:
            firstTime = timeObjects[0]
            lastTime = timeObjects[-1]
            diff = lastTime - firstTime
            if diff.total_seconds() >= 1:
                timeObjects = []
                return 'up'
            else:
                return 'right'
        return 'up'
        # if < 1 sec, count number, clear off, return count?1:'space',2:'left',3:'right'
    def do_GET(self):
        global station_status;
        print(self.path)
        path = serve_from + self.path
        if self.path == '/up':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Going up')
        elif self.path == '/request_station_status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # send json back
            status = json.dumps(station_status)
            self.wfile.write(bytes(status, 'UTF-8'))
        elif self.path == '/reset_station_status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            station_status = {}
        elif not os.path.abspath(path).startswith(serve_from):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'Private!')
        # File serving functionalities
        elif os.path.isdir(path):
            try:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(str(os.listdir(path)).encode())
            except Exception:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')
        else:
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)
            # error handling skipped
            except Exception:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')

    def do_POST(self):
        global station_status, code;
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'{"Viola station server": "Success"}')
        ## store the data
        try:
            body = body.decode()
            json_str = body[body.index('{'):body.rindex('}') + 1]
            json_value = json.loads(json_str)
            
            # Also store in local state, for requests from JS world
            summary_press = int(json_value['value']) + int(json_value['value1'])*2 + int(json_value['value2'])*4
            station_status[json_value['station-id']] = summary_press
            # start time loop
            lastCode = code
            code = self.check_time(datetime.datetime.now())
            code = 'space'
            # Test keytoggle mode
            #if code is 'up':
            #    keyUp(lastCode)
            #    keyDown('up')
            #else:
            #    keyUp(lastCode)
            #    keyDown(code)
                
            print (json_value['station-id'], summary_press,json_value['counter'], ' received at ', datetime.datetime.now(), code)
        except:
            print ("Error parsing json " + json_value)
        self.wfile.write(response.getvalue())

### CONFIGURATION
# Start server at this IP
host_ip = '10.41.2.37'
host_port = 8000
with open('config.json') as f:
  config = json.load(f)
  host_ip = config["server"]
  host_port = int(config["port"])

### Run
httpd = HTTPServer((host_ip, host_port), SimpleHTTPRequestHandler)
sa = httpd.socket.getsockname()
print ("Serving HTTP on", sa[0], "port", sa[1], "...")
httpd.serve_forever()