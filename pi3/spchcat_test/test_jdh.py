import os
import time
import signal
import subprocess

from gtts import gTTS
import asyncio

from function_jdh import listen, bulb_color_control

while True:
    # Standby mode - listen for "hello baby"
    # bulb - blue color
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bulb_color_control('blue'))
    loop.close()
    # bulb_color_control('blue')
    # user_input = listen(7)
    user_input = 'hello'

    if 'hello' in user_input or 'hallo' in user_input:  # and 'baby' in user_input:
        myobj = gTTS(text="Hello, good to see you again. How are you?", lang='en', slow=False)
        myobj = gTTS(text="H", lang='en', slow=False)
        myobj.save("temp.mp3")
        os.system("mpg321 temp.mp3")
        os.system("rm temp.mp3")
        print('hi~')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bulb_color_control('yellow'))
        loop.close()

        # Listen for user input for sentiment analysis
        user_input = listen(7)
        user_input = 'green'

        if 'green' in user_input:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(bulb_color_control('green'))
            loop.close()

        myobj2 = gTTS(text="Your command is..." + user_input, lang='en', slow=False)
        myobj2.save("temp.mp3")
        os.system("mpg321 temp.mp3")
        os.system("rm temp.mp3")