import os
import time
import signal
import subprocess

import asyncio
from itertools import cycle
import colorsys
import time

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import vlc
import random
from confluent_kafka import OFFSET_BEGINNING

from gtts import gTTS
import openai

openai.api_key = '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'

def chatbot(input_text, history=''):
    prompt_in = f'You:%s\Jarvis:' % (input_text)
    prompt_initial = 'The following is conversations between you and an AI assistant, Jarvis. Jarvis is very friendly and supportive. He can take care of your feeling.'
    
    if history == '':
        history = prompt_initial

    prompt = history + '\n' + prompt_in

    response = openai.Completion.create(
        model="text-curie-001",
        prompt=prompt,
        temperature=0.5,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=["You:"]
    )
    answer = response.choices[0].text.strip()
    history = prompt + answer
    
    # print('answer: %s\n\nhistory: %s' % (answer, history))    
    # print('answer: %s\n\nhistory: %s' % (answer, history))    
    return answer, history

def get_bulb_status():
    bulb = ['kasa --host 172.26.174.229 --type bulb state']

    # fd_open = subprocess.Popen(bulb, stdout=subprocess.PIPE,
    #                             text=True, shell=True, preexec_fn=os.setsid)
    fd_open = subprocess.Popen(bulb, stdout=subprocess.PIPE,
                               text=True, shell=True)

    state = fd_open.stdout.read().strip()
    state = state.split('\n')[2].strip().split(' ')[-1]

    return state

def speak(text):
    # print(text)
    myobj = gTTS(text=text, lang='en', slow=False)
    myobj.save("temp.mp3")
    os.system("mpg321 temp.mp3")
    os.system("rm temp.mp3")

def listen(t, wav_file=None):
    if wav_file is None:
        os.system('aplay beep2.wav')
        os.system('arecord --rate=16000 --duration=4 --file-type=wav tmp.wav')
    os.system('aplay beep_success.wav')

    # spchcat_start = ['cheetah_demo_mic --access_key Pz4Z3W+zC5NPN7TnXjdx20dZaixZrTXTXlwS1wNRNg66rA55CGU+gg==']
    spchcat_start = ['leopard_demo_file --access_key Pz4Z3W+zC5NPN7TnXjdx20dZaixZrTXTXlwS1wNRNg66rA55CGU+gg== --audio_paths tmp.wav']
    # spchcat_start = ['spchcat tmp.wav --language=en_US']
    fd_open = subprocess.Popen(spchcat_start, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True, shell=True)
    
    user_input = fd_open.stdout.read().strip()
    print(user_input)

    return user_input

def bulb_color_control(color):
    if color == 'blue':
        r, g, b = 0, 0, 1
    elif color == 'red':
        r, g, b = 1, 0, 0
    elif color == 'green':
        r, g, b = 0, 1, 0
    elif color == 'yellow':
        r, g, b = 1, 1, 0
    elif color == 'pink':
        r, g, b = 1.0, 204.0/255.0, 204.0/255.0
    elif color == 'white':
        r, g, b = 1, 1, 1

    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = int(h * 360)
    s = int(s * 100)
    v = int(v * 100)

    print(h, s, v)
    os.system('kasa --host 172.26.174.229 --type bulb hsv {} {} {}'.format(h, s, 10))
    time.sleep(1)

def play_music(emotion='anger'):
    emotion_dict=    {
    'anger' : ['road-trip', 'rock', 'rock-n-roll', 'hard-rock', 'alt-rock', 'metal', 'metal-misc', 'metalcore', 'rockabilly', 'psych-rock', 'punk', 'punk-rock','hardcore', 'hardstyle', 'heavy-metal'],
    'joy'  : ['hip-hop','party', 'club', 'disney', 'k-pop', 'kids','j-dance', 'j-idol', 'j-pop', 'j-rock', 'dub', 'dubstep', 'edm' , 'pop', 'pop-film', 'happy', 'salsa', 'samba', 'comedy', 'tango', 'techno' ],
    'sadness'  : ['acoustic', 'chill',  'sad', 'rainy-day'],
    'surprise' : ['sleep', 'study', 'classical', 'guitar', 'groove', 'new-age', 'piano', 'holidays', 'soul']}

    client_id = "e3959f978ad34cfeb2b13718df80cb45"
    client_secret = "0ca7e3dbc2d24b2da27e83e3938045ca"
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, 
                                                    client_secret=client_secret))
    if emotion == 'neutral':
        playlist_id = "https://open.spotify.com/playlist/37i9dQZF1DX0kbJZpiYdZl?si=0e1b86f7292c4712"
        results = spotify.playlist(playlist_id)
        i=0
        while results['tracks']['items'][i]['track']['preview_url'] == None:
            i+=1
        p = vlc.MediaPlayer(results['tracks']['items'][i]['track']['preview_url'])
        # p.audio_set_volume(50)
        print(p.play())
        lamp_blinking()
        print('done')
    else:
        spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, 
                                                            client_secret=client_secret))
        choice = random.choice(emotion_dict[emotion])
        print("The selected genre is "+ str(choice))
        if emotion == 'sadness':
            recommendations = spotify.recommendations(seed_genres=[choice], limit=30, max_tempo = 70)
        else:
            recommendations = spotify.recommendations(seed_genres=[choice], limit=30)
        i=0
        while recommendations['tracks'][i]['preview_url'] == None:
            i+=1

        p = vlc.MediaPlayer(recommendations['tracks'][i]['preview_url'])
        p.audio_set_volume(50)
        print(p.play())
        lamp_blinking()
        print('done')

def read_ccloud_config(config_file):
    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                conf[parameter] = value.strip()
    return conf

def reset_offset(consumer, partitions):
    for p in partitions:
        p.offset = OFFSET_BEGINNING
    consumer.assign(partitions)

def consume_kafka(consumer, reset = False, topic='emotion'):
    while True:
        msg = consumer.poll(1.0)
        if msg is not None and msg.error() is None:
            emotion = msg.value().decode('utf-8')
            break
    return emotion

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def produce_kafka(producer, data, topic='stt'):
    producer.poll(0)
    producer.produce(topic, data.encode('utf-8'), callback=delivery_report)
    return

def lamp_blinking():
    import numpy as np
    for _ in range(13):
        h = np.random.randint(1, 360)
        s = np.random.randint(1, 100)
        v = np.random.randint(10, 50)
        os.system('kasa --host 172.26.174.229 --type bulb hsv {} {} {}'.format(h, s, v))
        os.system('kasa --host 172.26.174.229 --type bulb off')
        os.system('kasa --host 172.26.174.229 --type bulb on')
    
    bulb_color_control('white')

if __name__=='__main__':
    # listen(1)
    history = ''
    while True:
        text_in = str(input())
        answer, history = chatbot(text_in, history)
        print('answer: %s' % (answer))
    # play_music()