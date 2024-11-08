from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit
import os
import json
from uuid import uuid4
from termcolor import colored, cprint
from flask_cors import CORS, cross_origin
from time import time

# Loads environment variables using dotenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from audio import audio

app = Flask(__name__)
CORS(app)
# Disables flask logging
#app.logger.disabled = True
import logging
#log = logging.getLogger('werkzeug')
#log.disabled = True

def default():
    return 'Success!'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.add_url_rule('/', view_func = default, methods = ['GET'])
socketio = SocketIO(app, cors_allowed_origins="*")
lastEntryTime = None

''' BEGIN WEBSOCKET CONNECTIONS AND ROUTES ------------------
'''

@socketio.on('connect')
def handle_connect(data):
    cprint(f'Client Connected', "green")
    print(data)
    socketio.emit('success', {})
    return 'Success'

@socketio.on('audioStream')
def handle_audio(data):
    global lastEntryTime

    cprint(f'Received Audio!', "cyan")
    output_text = audio.process_audiofile(data)
    print(output_text)
    cmd = ""

    if "enhance" in output_text or "enhanced" in output_text:
        cmd = "enhance"
    elif "go back" in output_text or "back" in output_text:
        cmd = "back"
    elif "sus" in output_text:
        cmd = "sus"
    elif "zoom" in output_text:
        cmd = "zoom"
    elif "reset" in output_text:
        cmd = "reset"
    elif "left" in output_text:
        cmd = "left"
    elif "delete" in output_text:
        cmd = "delete"
    elif "zoom" in output_text: cmd = "zoom"

    if cmd == "": 
        cprint(f"No commands detected")
        return 'Success'

    if lastEntryTime != None and time() - lastEntryTime < 1.5:
        cprint(f"Not invoking `{cmd}` command", "yellow")
        lastEntryTime = time()
        return

    cprint(f"Emitting `{cmd}` command", "green")
    lastEntryTime = time()
    emit('returnCommand', cmd, broadcast=True)

def handle_gestures():
    global lastEntryTime

    data = json.loads(request.data)
    gesture = data['gesture']

    cprint(f'Received gesture {gesture}!', "cyan")

    # Whitelisted states: 
    whitelisted_gestures = [
        "throw", "point", "swipe", "snap", "zoomin", "middle"
    ]

    if gesture not in whitelisted_gestures: 
        cprint(f'Invalid gesture {gesture}!', "red")
        return 'Success'

    if lastEntryTime != None and time() - lastEntryTime < 2:
        cprint(f"Not invoking `{gesture}` command", "yellow")
        lastEntryTime = time()
        return 'Success!'

    lastEntryTime = time()
    cprint(f"Emitting `{gesture}` gesture", "green")
    socketio.emit('returnCommand', gesture)
    return 'Success!'

app.add_url_rule('/sendGesture', view_func = handle_gestures, methods = ['POST'])

@socketio.on('disconnect')
def handle_disconnect():
    cprint(f'Client Disconnected', "red")

if __name__ == '__main__':
    print()
    cprint("--------------------------------------", "cyan")
    cprint("------Running websocket app-----------", "cyan")
    cprint("--------------------------------------", "cyan")
    print()

    socketio.run(app,host='0.0.0.0',port=8000)

