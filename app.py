from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit
import os
import json
from uuid import uuid4
from termcolor import colored, cprint

# Loads environment variables using dotenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

app = Flask(__name__)

def default():
    return 'Success!'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.add_url_rule('/', view_func = default, methods = ['GET'])
socketio = SocketIO(app)

''' BEGIN WEBSOCKET CONNECTIONS AND ROUTES ------------------
'''

@socketio.on('connection')
def handle_connect(data):
    cprint(f'Client Connected', "green")

@socketio.on('audioStream')
def handle_audio(data):
    cprint(f'Received Audio!', "green")
    print(data)

@socketio.on('disconnection')
def handle_disconnect():
    cprint(f'Client Disconnected', "red")

if __name__ == '__main__':
    print()
    cprint("--------------------------------------", "cyan")
    cprint("------Running websocket app-----------", "cyan")
    cprint("--------------------------------------", "cyan")
    print()

    socketio.run(app,host='0.0.0.0',port=8000)
