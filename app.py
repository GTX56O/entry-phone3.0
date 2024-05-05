import RPi.GPIO as GPIO
import time
from flask import Flask, render_template, Response
import cv2
import threading
import pyaudio
import socketio
import json
from picamera import PiCamera
import pygame
from threading import Timer
from flask_basicauth import BasicAuth
from mfrc522 import SimpleMFRC522
import datetime

app = Flask(__name__)
sio = socketio.Server(cors_allowed_origins='*')
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)


with open('config.json', 'r') as config_file:
    config = json.load(config_file)

basic_auth_username = config['BASIC_AUTH_USERNAME']
basic_auth_password = config['BASIC_AUTH_PASSWORD']
open_gate_pin = config['OPEN_GATE_PIN']
close_gate_pin = config['CLOSE_GATE_PIN']
ring_pin = config['RING_PIN']
gate_relay_pin = config['GATE_RELAY_PIN']
keypad_rows = config['KEYPAD_ROWS']
keypad_cols = config['KEYPAD_COLS']
host_ip = config['HOST_IP']
correct_pin = config['CORRECT_PIN']


pygame.mixer.init()
GPIO.setmode(GPIO.BCM)
GPIO.setup(open_gate_pin, GPIO.OUT)
GPIO.setup(close_gate_pin, GPIO.OUT)
GPIO.setup(ring_pin, GPIO.OUT)
GPIO.setup(gate_relay_pin, GPIO.OUT)
for row in keypad_rows:
    GPIO.setup(row, GPIO.OUT)
    GPIO.output(row, GPIO.HIGH)
for col in keypad_cols:
    GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_UP)


camera = PiCamera()
camera_active = False
camera_lock = threading.Lock()


audioElement = pygame.mixer.Sound


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()
audio_transmission_active = False

reader = SimpleMFRC522()
last_tag_id = None

def read_nfc():
    global last_tag_id
    try:
        while True:
            id, text = reader.read()
            if id != last_tag_id:
                print(f"Nowy tag NFC wykryty: {text}")
                handle_nfc_tag(text)
                last_tag_id = id
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()

# Obsługa odczytanego tagu NFC
def handle_nfc_tag(tag_data):
    global entered_pin
    if tag_data.isdigit() and len(tag_data) == 4:
        entered_pin = tag_data
        open_gate_relay()
    else:
        log_error("Nieprawidłowy format danych na etykiecie NFC.")


nfc_thread = threading.Thread(target=read_nfc)
nfc_thread.start()


def generate_frame():
    while True:
        with camera_lock:
            if camera_active:
                camera.capture('frame.jpg')
                frame_data = open('frame.jpg', 'rb').read()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
            else:
                time.sleep(1)


def audio_transmission():
    global audio_transmission_active
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=CHUNK)

    while audio_transmission_active:
        data = stream.read(CHUNK)
        sio.emit('audio_data', {'data': data}, room='audio')


def handle_keypad_input(key):
    global entered_pin
    if key == "*":
        answer_call()
    elif key == "#":
        if entered_pin == correct_pin:
            open_gate_relay()
            entered_pin = ""
        else:
            log_error("Nieprawidłowy pin. Brama nie zostanie otwarta.")
    else:
        entered_pin += key
        pygame.mixer.Sound.play(keypad_press_sound)
        print(f"Wprowadzony pin: {entered_pin}")


def keypad_listener():
    try:
        while True:
            for row in range(len(keypad_rows)):
                GPIO.output(keypad_rows[row], GPIO.LOW)
                for col in range(len(keypad_cols)):
                    if GPIO.input(keypad_cols[col]) == GPIO.LOW:
                        key = str((row * len(keypad_cols)) + col + 1)
                        handle_keypad_input(key)
                        while GPIO.input(keypad_cols[col]) == GPIO.LOW:
                            time.sleep(0.1)
                GPIO.output(keypad_rows[row], GPIO.HIGH)
    except KeyboardInterrupt:
        GPIO.cleanup()


keypad_thread = threading.Thread(target=keypad_listener)
keypad_thread.start()


@app.route("/")
@basic_auth.required
def index():
    return render_template("index.html")


@app.route("/open_gate")
@basic_auth.required
def open_gate():
    log_action("Otwieranie bramy")
    GPIO.output(open_gate_pin, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(open_gate_pin, GPIO.LOW)
    return "Otwieranie bramy"


@app.route("/close_gate")
@basic_auth.required
def close_gate():
    log_action("Zamykanie bramy")
    GPIO.output(close_gate_pin, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(close_gate_pin, GPIO.LOW)
    return "Zamykanie bramy"


@app.route("/answer_call")
@basic_auth.required
def answer_call():
    log_action("Rozpoczęto połączenie")
    pygame.mixer.Sound.play(ringing_sound)
    GPIO.output(ring_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(ring_pin, GPIO.LOW)
    time.sleep(1)
    GPIO.output(ring_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(ring_pin, GPIO.LOW)

    global audio_transmission_active, camera_active

    with camera_lock:
        camera.start_preview()
        camera_active = True

    timer = Timer(30, answer_call_timeout)
    timer.start()

    return "Rozpoczęto połączenie."

@app.route('/camera_feed')
@basic_auth.required
def camera_feed():
    if audio_transmission_active:
        return Response(generate_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Brak audio."


@app.route('/open_gate_relay')
@basic_auth.required
def open_gate_relay():
    log_action("Otwieranie furtki")
    pygame.mixer.Sound.play(gate_open_sound)
    GPIO.output(gate_relay_pin, GPIO.HIGH)
    time.sleep(5)
    GPIO.output(gate_relay_pin, GPIO.LOW)
    return "Otwieranie furtki"


@app.route('/end_call')
@basic_auth.required
def end_call():
    log_action("Zakończono połączenie audio.")
    global audio_transmission_active, camera_active
    audio_transmission_active = False
    camera_active = False
    with camera_lock:
        camera.stop_preview()
    return "Zakończono połączenie audio."


def start_audio_transmission():
    global audio_transmission_active
    audio_transmission_active = True
    threading.Thread(target=audio_transmission).start()
    print("Rozpoczęto transmisję audio.")


def answer_call_timeout():
    if audio_transmission_active:
        end_call()
    else:
        log_error("Nikt nie odebrał. Zakończono połączenie.")


def log_action(action):
    with open('log.txt', 'a') as log_file:
        log_file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {action}\n")


def log_error(error):
    with open('log.txt', 'a') as log_file:
        log_file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Błąd - {error}\n")

if __name__ == "__main__":
    app.run(host=host_ip, port=5000)
