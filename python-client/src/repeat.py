import time
import json
from adbutils import adb

d = adb.device(serial="localhost:5555")

def screenshot(path):
    remote_tmp_path = "/data/local/tmp/screenshot.png"
    d.shell(["rm", remote_tmp_path])
    d.shell(["screencap", "-p", remote_tmp_path])
    d.sync.pull(remote_tmp_path, 'run/'+path)


# @sio.on('Click')
def on_click(data):
    print(data)
    screenshot("r_click_"+str(data["timestamp"])+".png")
    d.click(data["x"],data["y"])


# @sio.on('KeyInput')
def on_input(data):
    print(''.join([chr(data["keycode"])]))
    d.send_keys(''.join([chr(data["keycode"])]))


# @sio.on('KeyEvent')
def on_event(data):
    print(data)
    d.keyevent(data["keycode"])


# @sio.on('Swipe')
def on_swipe(data):
    print(data)
    screenshot("r_swipe_"+str(data["end"]["timestamp"])+".png")
    d.swipe(data["start"]["x"],data["start"]["y"],data["end"]["x"],data["end"]["y"],(data["end"]["timestamp"]-data["start"]["timestamp"])/1000)

def read_file(filename):
	with open(filename) as f:
		data = json.load(f)
		for action in data:
			print(action)
			if(action["action"] == "click"):
				on_click(action["params"])
				time.sleep(3)
			if(action["action"] == "keyInput"):
				on_input(action["params"])
				time.sleep(0.2)
			if(action["action"] == "keyEvent"):
				on_event(action["params"])
				time.sleep(1)
			if(action["action"] == "swipe"):
				on_swipe(action["params"])
				time.sleep(1.5)
	f.close()
