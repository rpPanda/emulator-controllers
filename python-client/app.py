import socketio
import time

from adbutils import adb

d = adb.device('localhost:5555')

sio = socketio.Client()

r = d.screenrecord(no_autostart=True)

def screenshot(path):
    remote_tmp_path = "/data/local/tmp/screenshot.png"
    d.shell(["rm", remote_tmp_path])
    d.shell(["screencap", "-p", remote_tmp_path])
    d.sync.pull(remote_tmp_path, path)


@sio.event
def connect():
    print('connection established')

@sio.on('Start')
def on_start(data):
    print("Start")
    # r.start()

@sio.on('Stop')
def on_stop(data):
    # r.stop()
    print("Stop")
    

@sio.on('Click')
def on_click(data):
    print(data)
    screenshot("click_"+str(data["timestamp"])+".png")
    d.click(data["x"],data["y"])
    

@sio.on('KeyInput')
def on_click(data):
    print(''.join([chr(data["keycode"])]))
    d.send_keys(''.join([chr(data["keycode"])]))


@sio.on('KeyEvent')
def on_click(data):
    print(data)
    d.keyevent(data["keycode"])


@sio.on('Swipe')
def on_click(data):
    print(data)
    screenshot("swipe_"+str(data["end"]["timestamp"])+".png")
    d.swipe(data["start"]["x"],data["start"]["y"],data["end"]["x"],data["end"]["y"],(data["end"]["timestamp"]-data["start"]["timestamp"])/1000)

@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://localhost:4000')

stream = d.shell("screenrecord /sdcard/s.mp4", stream=True)
time.sleep(3) # record for 3 seconds
with stream:
    stream.send("\003") # send Ctrl+C
    stream.read_until_close()

start = time.time()
print("Video total time is about", time.time() - start)
d.sync.pull("/sdcard/s.mp4", "s.mp4") # pulling video
print("hi")
sio.wait()
