from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit
import os
import json
from uuid import uuid4

# Loads environment variables using dotenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

app.add_url_rule('/', view_func = default, methods = ['GET'])

''' BEGIN WEBSOCKET CONNECTIONS AND ROUTES ------------------
'''

connections =  []

@socketio.on('connect')
def handle_connect(data):
    global connections
    user_id = int(request.headers['Userid'])
    connection_type = request.headers['Connectiontype']

    connections.append({
        'sid': request.sid,
        'connection_type': connection_type,
        'user_id': user_id
    })

    print(f'Client Connected, total clients: {len(connections)}')

@socketio.on('disconnect')
def handle_disconnect():
    global connections
    sid = request.sid
    connections = [i for i in connections if i['sid'] != sid]

    print(f'Client Disconnected, total clients: {len(connections)}')

if __name__ == '__main__':
    print("--------------------------------------")
    print("------Running websocket app-----------")
    print("--------------------------------------")

    socketio.run(app,host='0.0.0.0',port=8000)
