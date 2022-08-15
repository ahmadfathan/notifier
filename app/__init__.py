import sys
from http import HTTPStatus
from os import path
from flask import Flask, jsonify, request
from flask_cors import CORS
import paho.mqtt.publish as publish

sys.path.insert(0, path.dirname(path.dirname(__file__)))

import auth

app = Flask(__name__)
CORS(app)

import confuse

config = confuse.Configuration('App', __name__, read=False)
config_path = path.join(path.dirname(path.dirname(__file__)), 'config.yaml')

config.set_file(config_path, base_for_paths=True)

MQTT_SERVER = config['MQTT_SERVER'].get()
MQTT_PORT = config['MQTT_PORT'].get()
MQTT_USER = config['MQTT_USER'].get()
MQTT_PASSWORD = config['MQTT_PASSWORD'].get()

RTTTL = config['RTTTL'].get()

WHITELISTED_USERS = config['WHITELISTED_USERS'].get()

def create_response(code, is_success, message, data=None):
    resp = {
        'is_success': is_success,
        'message': message
    }

    if data is not None: resp['results'] = {'data': data}

    return jsonify(resp), code

def mqtt_publish(topic, payload):
    publish.single( 
        topic, 
        payload=payload, 
        qos=2, 
        hostname=MQTT_SERVER, port=MQTT_PORT
    )

@app.route("/", methods=['GET'])
def root():
    return create_response(HTTPStatus.OK, True, "It's working!!")

@app.route("/auth/login", methods=['POST'])
def login():
    user = request.form['user']

    if not user:
        return create_response(HTTPStatus.BAD_REQUEST, True, "Bad parameter")

    token = auth.encode_auth_token(user)

    return create_response(HTTPStatus.OK, True, "OK", data={'token': token})

@app.route("/play", methods=['POST'])
def play():
    url = request.form['url']
    topic = request.form['topic']
        
    if not url or not topic:
        return create_response(HTTPStatus.BAD_REQUEST, True, "Bad parameter")

    mqtt_publish(f"{topic}/play", url)
    return create_response(HTTPStatus.OK, True, "OK")

@app.route("/stream", methods=['POST'])
def stream():
    return jsonify(request.headers.keys())

    token = request.headers['HTTP_AUTHORIZATION']
    url = request.form['url']
    topic = request.form['topic']
    
    if not url or not topic or not token:
        return create_response(HTTPStatus.BAD_REQUEST, True, "Bad parameter")

    if not len(token.split(' ')) == 2:
        return create_response(HTTPStatus.BAD_REQUEST, True, "Authentication failed")

    ret, result = auth.decode_auth_token(token.split(' ')[1])

    if not ret: 
        return create_response(HTTPStatus.BAD_REQUEST, True, result)

    user = result

    if not user in WHITELISTED_USERS:
        return create_response(HTTPStatus.BAD_REQUEST, True, "User not allowed")

    mqtt_publish(f"{topic}/stream", url)
    return create_response(HTTPStatus.OK, True, "OK")

@app.route("/volume", methods=['POST'])
def volume():
    topic = request.form['topic']
    volume = request.form['volume']

    if not volume or not topic:
        return create_response(HTTPStatus.BAD_REQUEST, True, "Bad parameter")

    mqtt_publish(f"{topic}/volume", volume)
    return create_response(HTTPStatus.OK, True, "OK")

@app.route("/stop", methods=['POST'])
def stop():

    mqtt_publish("test/stop", " ")
    return create_response(HTTPStatus.OK, True, "OK")

