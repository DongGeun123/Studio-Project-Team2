import os
import time
import signal
import subprocess
from confluent_kafka import Consumer, Producer
import argparse

from gtts import gTTS
import asyncio

from function import *

parser = argparse.ArgumentParser()
parser.add_argument("--reset", action="store_true")
args = parser.parse_args()

props = read_ccloud_config("client.properties")
props["group.id"] = "python-group-1"
props["auto.offset.reset"] = "earliest"

consumer = Consumer(props)

if args.reset:
    consumer.subscribe(["emotion"], on_assign=reset_offset)
else:
    consumer.subscribe(["emotion"])

props = read_ccloud_config("client.properties")
props["group.id"] = "python-group-1"
props["bootstrap.servers"] = 'pkc-419q3.us-east4.gcp.confluent.cloud:9092'

producer = Producer(props)

while True:
    # Standby mode - listen for "hello baby"
    # green - green color

    if not get_bulb_status() == 'OFF':
        bulb_color_control('green')

    os.system('porcupine_demo_mic --output_path /home/pi3/spchcat_test/tmp.wav  --access_key Pz4Z3W+zC5NPN7TnXjdx20dZaixZrTXTXlwS1wNRNg66rA55CGU+gg== --keywords jarvis')
    # user_input = listen(7, 'tmp.wav')
    # user_input = 'hello'

    # if 'hello' in user_input or 'hallo' in user_input or 'pie' in user_input:
    speak("Hello, good to see you again. How are you?")
    bulb_color_control('white') # Ready to listen
    
    # Listen for user input for sentiment analysis
    user_input = listen(7)
    # user_input = "I feel great!"
    # os.system('aplay beep_success.wav')
    produce_kafka(producer, user_input, topic='stt')
    emotion = consume_kafka(consumer, topic='emotion')

    emotion_to_color = {
        'anger': 'red',
        'joy': 'pink',
        'sadness': 'blue',
        'surprise': 'yellow',
        'neutral': 'white'
    }

    emotion_to_speak ={
        'anger': 'It seems like you are angry.',
        'joy': 'It seems like you are happy.',
        'sadness': 'It seems like you are sad.',
        'surprise': 'It seems like you are surprised.',
        'neutral': 'It seems like you are ok.'
    }
    
    speak(emotion_to_speak[emotion])
    bulb_color_control(emotion_to_color[emotion])
    speak("What can I do for you?")

    history = ''
    # Free Talking with chatbot powered by openAI
    while True:
        user_input = listen(7)

        if "stop" in user_input.lower() or "bye" in user_input.lower() or "by" in user_input.lower():
            speak("Good bye.")
            break

        if len(user_input) == 0:
            speak("No Response. I will be waiting for you.")
            break

        if "please" in user_input.lower():
            # speak("What do you want to do?")
           
            # os.system('aplay beep2.wav')
            # user_input = listen(7)
            if 'turn' in user_input.lower() and 'on' in user_input.lower():
                
                if get_bulb_status() == 'ON':
                    speak("The light is already on.")
                else:
                    speak("I am turning on the light for you.")
                    os.system('kasa --host 172.26.174.229 --type bulb on')
                break

            elif 'off' in user_input or 'of' in user_input:
                if get_bulb_status() == 'OFF':
                    speak("The light is already off.")
                else:
                    speak("I am turning off the light for you.")
                    os.system('kasa --host 172.26.174.229 --type bulb off')
                break

            elif 'music' in user_input.lower() or 'play' in user_input.lower() or 'musi' in user_input.lower():
                # Play music based on sentiment analysis
                speak("I am playing music for you based on your emotion. Please enjoy it.")
                play_music(emotion)
                
                # speak("I hope you feel better now. Goodbye.")
                break

            else:
                answer, history = chatbot(user_input, history)
                if len(history) > 500:
                    history = ''
                    
                # os.system('aplay beep_success.wav')
                print('-------------------------------------------')
                print('[Input] ' + user_input)
                print('[Response] '+ answer)
                # print('[History] '+ history)
                print('-------------------------------------------')
                speak(answer)

                # os.system('aplay beep_fail.wav')
                # speak("Sorry, I don't understand.")
                # if i == 2:
                #     speak("Goodbye.")
                # else:
                #     speak("Please try again.")
                #     user_input = listen(7)

        else:
            answer, history = chatbot(user_input, history)
            if len(history) > 500:
                history = ''
                
            # os.system('aplay beep_success.wav')
            print('-------------------------------------------')
            print('[Input] ' + user_input)
            print('[Response] '+ answer)
            # print('[History] '+ history)
            print('-------------------------------------------')
            speak(answer)