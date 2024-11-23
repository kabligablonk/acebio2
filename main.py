import RPi.GPIO as GPIO
import time
import json
import os
import PySimpleGUI as sg
import Data

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)

led_pins = [5, 6, 13, 19, 26, 12, 16, 20]

# State management
state_file = 'state.json'

def read_state():
    default_state = {'dictionary_index': 1, 'submit_pressed': False}
    if os.path.exists(state_file) and os.path.getsize(state_file) > 0:
        with open(state_file, 'r') as f:
            try:
                state = json.load(f)
                for key in default_state:
                    if key not in state:
                        state[key] = default_state[key]
                return state
            except json.JSONDecodeError:
                return default_state
    else:
        return default_state

def write_state(state):
    with open(state_file, 'w') as f:
        json.dump(state, f)

state = read_state()
dictionary_index = state['dictionary_index']
submit_pressed = state['submit_pressed']

def increment():
    global dictionary_index
    dictionary_index += 1
    write_state({'dictionary_index': dictionary_index, 'submit_pressed': submit_pressed})
    led_on_off()

def decrement():
    global dictionary_index
    if dictionary_index > 1:
        dictionary_index -= 1
        write_state({'dictionary_index': dictionary_index, 'submit_pressed': submit_pressed})
        led_on_off()

def submit():
    global submit_pressed
    submit_pressed = True
    write_state({'dictionary_index': dictionary_index, 'submit_pressed': submit_pressed})
    led_on_off()

def led_on_off():
    for pin in led_pins:
        GPIO.output(pin, GPIO.LOW)
    for i in range(dictionary_index):
        if i < len(led_pins):
            GPIO.output(led_pins[i], GPIO.HIGH)

def debounce(pin):
    time.sleep(0.05)
    return GPIO.input(pin) == GPIO.LOW

# GUI setup
sg.theme('Dark Gray 13')
information = Data.information

def get_info(index):
    keys = list(information.keys())
    if index < len(keys):
        key = keys[index]
        try:
            return int(information[key])
        except Exception:
            return information[key]
    else:
        return "Index out of range"

layout = [
    [sg.Text("Index (Part name)"), sg.Input(key='-INPUT-')],
    [sg.Text("Results (Part info):", size=(0, 10), key='-PART-'), sg.Text("", key='-RESULT-', size=(50, 10), font=(32),)],
    [sg.Button("Get Info"), sg.Button("Exit")]
]

window = sg.Window("Group 3 ACEBIO", layout, size=(700, 400), resizable=True)

try:
    prev_input_17 = prev_input_27 = prev_input_22 = GPIO.HIGH
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == "Get Info" or submit_pressed:
            try:
                index = int(values['-INPUT-'])
                result = get_info(index)
                window['-RESULT-'].update(result)
                window['-INPUT-'].update("")
                submit_pressed = False
                write_state({'dictionary_index': dictionary_index, 'submit_pressed': submit_pressed})
            except ValueError as e:
                sg.popup_error(f"Enter a valid index. \n Error: {e}")

        state = read_state()
        dictionary_index = state['dictionary_index']
        if dictionary_index is not None:
            window['-INPUT-'].update(dictionary_index)

        input_17 = GPIO.input(17)
        input_27 = GPIO.input(27)
        input_22 = GPIO.input(22)

        if input_17 == GPIO.LOW and prev_input_17 == GPIO.HIGH and debounce(17):
            increment()
        elif input_27 == GPIO.LOW and prev_input_27 == GPIO.HIGH and debounce(27):
            decrement()
        elif input_22 == GPIO.LOW and prev_input_22 == GPIO.HIGH and debounce(22):
            submit()

        prev_input_17 = input_17
        prev_input_27 = input_27
        prev_input_22 = input_22

        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
finally:
    window.close()
    GPIO.cleanup()