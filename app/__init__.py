from http import HTTPStatus
from os import path
from flask import Flask, jsonify, request
from flask_cors import CORS
import paho.mqtt.publish as publish

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

def create_response(code, is_success, message, data=None):
    resp = {
        'is_success': is_success,
        'message': message
    }

    if data is not None: resp['data'] = data

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

@app.route("/play", methods=['GET'])
def play():
    url = request.args.get('url')
    topic = request.args.get('topic')
        
    mqtt_publish(f"{topic}/play", url)
    return create_response(HTTPStatus.OK, True, "OK")

@app.route("/stream", methods=['GET'])
def stream():
    url = request.args.get('url')
    topic = request.args.get('topic')
    
    mqtt_publish(f"{topic}/stream", url)
    return create_response(HTTPStatus.OK, True, "OK")

@app.route("/volume", methods=['GET'])
def volume():
    topic = request.args.get('topic')
    volume = request.args.get('volume')

    mqtt_publish(f"{topic}/volume", volume)
    return create_response(HTTPStatus.OK, True, "OK")

@app.route("/stop", methods=['GET'])
def stop():

    mqtt_publish("test/stop", " ")
    return create_response(HTTPStatus.OK, True, "OK")

