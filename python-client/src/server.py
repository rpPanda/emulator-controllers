import socketio
import time
from adbutils import adb
from aiohttp import web
import json
from repeat import read_file
import base64
sio = socketio.AsyncServer( cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

d = adb.device('localhost:5555')
r = d.screenrecord(no_autostart=True)

actions=[]
action = ""
paramStart={}
paramEnd={}

asciiToAdb={
8: 67, # Backspace
9: 61, # Tab
13: 66, # Enter
27: 4, #Escape: Back
37: 21, # Left arrow
38: 19, # Up arrow
39: 22, # Right arrow
40: 20, # Down arrow
46: 67, #Delete
}

@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.on('TouchDownMessage')
def on_touch_down(sid,data):
    global action
    global paramStart
    print("Click")
    action="Click"
    paramStart = data

@sio.on('TouchMoveMessage')
def on_touch_move(sid,data):
    global action
    global paramEnd
    action = "Swipe"
    paramEnd = data

@sio.on('TouchUpMessage')
async def on_touch_up(sid,data):
    global action
    global actions
    global paramStart
    global paramEnd
    if (action=="Click"):
        screenshot("test/click_"+str(paramStart["timestamp"])+".png")
        d.click(paramStart["x"],paramStart["y"])
        actions.append({"action":"click","params": paramStart})
        with open("test/click_"+str(paramStart["timestamp"])+".png", "rb") as image_file:
            await sio.emit('Clicked',{"action":"click","params": paramStart,"image":base64.b64encode(image_file.read()).decode('utf-8')})

    else:
        data = {"start": paramStart, "end": paramEnd}
        screenshot("test/swipe_"+str(data["end"]["timestamp"])+".png")
        d.swipe(data["start"]["x"],data["start"]["y"],data["end"]["x"],data["end"]["y"],(data["end"]["timestamp"]-data["start"]["timestamp"])/1000)
        actions.append({"action":"swipe","params":data})
        with open("test/swipe_"+str(paramEnd["timestamp"])+".png", "rb") as image_file:
            await sio.emit('Swiped',{"action":"swipe","params": data,"image":base64.b64encode(image_file.read()).decode('utf-8')})

@sio.on('KeyEventMessage')
def on_key_event(sid,data):
    global actions
    keycode = asciiToAdb[data["keycode"]]
    print(keycode)
    d.keyevent(keycode)
    actions.append({"action":"keyEvent","params": data})

@sio.on('KeyInputMessage')
def on_key_input(sid,data):
    global actions
    print(''.join([chr(data["keycode"])]))
    d.send_keys(''.join([chr(data["keycode"])]))

@sio.on('StartRec')
def on_start(sid,data):
    print("Start")
    # r.start()

@sio.on('StopRec')
def on_stop(sid,data):
    global actions
    # r.stop()
    print("Stop")
    with open('emulator_create.json', 'w') as fout:
        json.dump(actions, fout)
    actions = []

@sio.on('Repeat')
def on_stop(sid,data):
    print("Repeat")
    read_file('emulator_create.json')

# @sio.on('Click')
# def on_click(sid,data):
#     print(data)
#     screenshot("click_"+str(data["timestamp"])+".png")
#     d.click(data["x"],data["y"])


# @sio.on('KeyInput')
# def on_click(sid,data):
#     print(''.join([chr(data["keycode"])]))
#     d.send_keys(''.join([chr(data["keycode"])]))


# @sio.on('KeyEvent')
# def on_click(sid,data):
#     print(data)
#     d.keyevent(data["keycode"])


# @sio.on('Swipe')
# def on_click(sid,data):
#     print(data)
#     screenshot("swipe_"+str(data["end"]["timestamp"])+".png")
#     d.swipe(data["start"]["x"],data["start"]["y"],data["end"]["x"],data["end"]["y"],(data["end"]["timestamp"]-data["start"]["timestamp"])/1000)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)

def screenshot(path):
    remote_tmp_path = "/data/local/tmp/screenshot.png"
    d.shell(["rm", remote_tmp_path])
    d.shell(["screencap", "-p", remote_tmp_path])
    d.sync.pull(remote_tmp_path, path)


if __name__ == '__main__':
    web.run_app(app,port=4000)


# @sio.event
# def disconnect(sid):
#     print('disconnected from server')

# sio.connect('http:#localhost:4000')

# stream = d.shell("screenrecord /sdcard/s.mp4", stream=True)
# time.sleep(3) # record for 3 seconds
# with stream:
#     stream.send("\003") # send Ctrl+C
#     stream.read_until_close()

# start = time.time()
# print("Video total time is about", time.time() - start)
# d.sync.pull("/sdcard/s.mp4", "s.mp4") # pulling video
# print("hi")
# sio.wait()
