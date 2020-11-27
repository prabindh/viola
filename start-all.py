import webbrowser
import os
import json

#precocious loading
# Start server at this IP
host_ip = '10.41.2.37'
host_port = 8000
with open('config.json') as f:
  config = json.load(f)
  host_ip = config["server"]
  host_port = config["port"]

url = "http:///"+host_ip + ":" + host_port + "//kelvi2.html"
#url = "http:///chromedino.com/"
#url = "http:///"+host_ip + ":" + host_port + "//game/game.html"
#webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open(url)

os.system("python server.py")

