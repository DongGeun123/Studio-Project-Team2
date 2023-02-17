import os
import time
import signal
import subprocess

from gtts import gTTS
import asyncio

from function import listen, bulb_color_control, play_music, speak


if __name__ == "__main__":
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

    # produce_kafka(producer, stt_result, topic='stt')
    # emotion = consume_kafka(consumer, topic='emotion')

    while True:
        # Standby mode - listen for "hello baby"
        # bulb - blue color
        bulb_color_control('pink')
        user_input = listen(7)
        user_input = 'hello'

        if 'hello' in user_input or 'hallo' in user_input:# and 'baby' in user_input:
            speak("Hello, good to see you again. How are you?")
            bulb_color_control('white') # Ready to listen
            
            # Listen for user input for sentiment analysis
            # user_input = listen(7)
            user_input = "I feel great!"
            produce_kafka(producer, stt_result, topic='stt')
            emotion = consume_kafka(consumer, topic='emotion')

            emotion_to_color = {
                'anger': 'red',
                'joy': 'green',
                'sadness': 'blue',
                'surprise': 'yellow'
            }
            
            # Play music based on sentiment analysis
            speak("I am playing music for you based on your emotion. Please enjoy it.")
            # emotion = 'anger'
            play_music(emotion)
            
            speak("I hope you feel better now. Do you want to play a game?")