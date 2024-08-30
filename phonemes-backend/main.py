from flask import Flask, jsonify
# import random
import pyaudio
import wave
# from openai import OpenAI
from flask_cors import CORS
from dotenv import load_dotenv
import os
from groq import Groq
app = Flask(__name__)
cors = CORS(app, supports_credentials=True)
load_dotenv()
OPEN_API_KEY = os.getenv('OPEN_API_KEY')
COUPLED = ""
SOUND_REFERENCE = {
    'S': 'SH',
    'F': 'TH',
    'L': 'R',
    'B': 'V',
    'P': 'F',
    'T': 'D',
    'A': 'E',  # Added
    'Z': 'S'   # Added
}

IMAGE ={
     'A' : 'https://png.pngtree.com/png-vector/20231017/ourmid/pngtree-fresh-apple-fruit-red-png-image_10203073.png',
     "Z" : 'https://pngimg.com/uploads/zebra/zebra_PNG95977.png'
}

PRONUNCIATION = {
    "sunday": "sʌn.deɪ",
    "free": "friː",
    "love": "lʌv",
    "boat": "boʊt",
    "pen": "pen",
    "tree": "triː",
    "apple": "ˈæp.əl",   # Added
    "ball": "bɔːl",      # This is already included
    "zebra": "ˈziː.brə"  # Added
}


LETTERS = ['S', 'F', 'L', 'B', 'P', 'T', 'A', 'Z']  # Added 'A', 'Z'

EXAMPLE = {
    'S': 'sunday',
    'F': 'free',
    'L': 'love',
    'B': 'boat',
    'B2':'ball',
    'P': 'pen',
    'T': 'tree',
    'A': 'apple',  # Added
    'Z': 'zebra'   # Added
}


REMEDY = {
    'P': ['Put your lips together to make the sound. Vocal cords don’t vibrate for voiceless sounds.'],
    'B': ['Put your lips together to make the sound.'],
    'B2': ['Put your lips together to make the sound.'],
    'M': ['Put your lips together to make the sound. Air flows through your nose.'],
    'W': ['Put your lips together and shape your mouth like you are saying "oo".'],
    'F': ['Place your bottom lip against your upper front teeth. Top teeth may be on your bottom lip.'],
    'V': ['Place your bottom lip against your upper front teeth. Top teeth may be on your bottom lip.'],
    'S': ["Keep your teeth close together to make the sound. The ridge right behind your two front teeth is involved. The front of your tongue is used. Vocal cords don’t vibrate for voiceless sounds."],
    'Z': ['Keep your teeth close together to make the sound. The ridge right behind your two front teeth is involved. The front of your tongue is used.'],
    'th': ['Place your top teeth on your bottom lip and let your tongue go between your teeth for the sound. The front of your tongue is involved.'],
    'TH': ['Place your top teeth on your bottom lip and let your tongue go between your teeth for the sound (as in thin). The front of your tongue is involved. The front of your tongue is used.'],
    'NG': ['Air flows through your nose.'],
    'SING': ['Air flows through your nose.'],
    'L': ['The ridge right behind your two front teeth is involved. The front of your tongue is used.'],
    'T': ["The ridge right behind your two front teeth is involved. The front of your tongue is used. Vocal cords don’t vibrate for voiceless sounds."],
    'D': ['The ridge right behind your two front teeth is involved. The front of your tongue is used.'],
    'CH': ['The front-roof of your mouth is the right spot for the sound. The front of your tongue is used.'],
    'J': ['The front-roof of your mouth is the right spot for the sound. The front of your tongue is used.'],
    'SH': ['The front-roof of your mouth is the right spot for the sound. The front of your tongue is used.'],
    'ZH': ['The front-roof of your mouth is the right spot for the sound. The front of your tongue is used.'],
    'K': ["The back-roof of your mouth is the right spot for the sound. The back of your tongue is used. Vocal cords don’t vibrate for voiceless sounds."],
    'G': ['The back-roof of your mouth is the right spot for the sound. The back of your tongue is used.'],
    'R': ['The back-roof of your mouth is the right spot for the sound. The back of your tongue is used.'],
    'Y': ['The front of your tongue is used.'],
    'H': ['Your lungs provide the airflow for every sound, especially this one.'],
    'A': [
        'Open your mouth wide with your tongue flat at the bottom, as in "apple".',
        'Open your mouth wide and pull your tongue back slightly, as in "father".'
    ]  # Added remedies for 'A'
}



def check(word_given, word_recieved, check_for):
        k=0
        while k<len(word_recieved) and word_recieved[k]==' ':
             k+=1
        word_recieved=word_recieved[k:]
        for i in range(k,len(word_recieved)):
              if word_recieved[i]=='.' or word_recieved[i]=='\n' or word_recieved[i]==' ' or word_recieved[i]=='' or word_recieved[i]=='!':
                    word_recieved=word_recieved[0:i]
                    break
        print(word_given,word_recieved,check_for)
        if word_recieved[0:len(SOUND_REFERENCE[check_for])] == SOUND_REFERENCE[check_for]:
            #print(word_recieved[len(SOUND_REFERENCE[check_for]):],word_given[len(check_for):])
            if word_recieved[len(SOUND_REFERENCE[check_for]):]==word_given[len(check_for):]:

                 return 20
            else:
                 print(word_recieved,word_given)
                 return 0

            #return [0,REMEDY[check_for]]
        elif word_recieved[0:len(check_for)]==word_given[0:len(check_for)]:
            if word_recieved[len(check_for):]==word_given[len(check_for):]:
                 return 100
            else:
                 return 75
        else:
            # print('dasd')
            return 0


# import os




# with open(filename, "rb") as file:
#     transcription = client.audio.transcriptions.create(
#       file=(filename, file.read()),
#       model="whisper-large-v3",
#       response_format="verbose_json",
#     )
#     print(transcription.text)
      
@app.route('/record', methods=["GET"])
def record():
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 5
    filename = "output.wav"

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # client = OpenAI(api_key=OPEN_API_KEY)
    client = Groq(api_key=OPEN_API_KEY)

    # audio_file = open(, "rb")
    with open("output.wav", "rb") as file:
        transcription = client.audio.transcriptions.create(
        file=(filename, file.read()),
        model="distil-whisper-large-v3-en",
        response_format="verbose_json",
        )
    print(transcription.text)
    percentage = check(EXAMPLE[COUPLED].upper(), transcription.text.upper(), COUPLED.upper())

    print(percentage)
    word_percentage = {
        "transcript": transcription.text,
        "percentage": percentage
    }
    return jsonify(word_percentage)


@app.route("/remedy/<int:averagePercentage>", methods=["GET", "POST"])
def remedy(averagePercentage):
    if (averagePercentage<=50):
        result = {
            "remedy":REMEDY[COUPLED]
        }
    else:
        result = {
            "remedy":""
        }

    return jsonify(result)


@app.route("/test/<lettergiven>")
def test(lettergiven):
    print(lettergiven)
    global COUPLED
    COUPLED = ""
    COUPLED = lettergiven
    if lettergiven=="B":
         
        word_data = {
            "word1": "ball",
            "letter": 'B',
            "pronunciation":"bɔːl",
            "image_link": 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Soccerball.svg/500px-Soccerball.svg.png'

        }
    else:
         word_data = {
        "word1": EXAMPLE[COUPLED],
        "letter": COUPLED,
        "pronunciation": PRONUNCIATION[EXAMPLE[COUPLED[0]]],
        "image_link": IMAGE[COUPLED]

    }
         
    print(COUPLED)
    return jsonify(word_data)

@app.route("/generate_word/<lettergiven>")
def generate_word(lettergiven):
    print(lettergiven)
    global COUPLED
    COUPLED = ""
    COUPLED = lettergiven

    word_data = {
        "word1": EXAMPLE[COUPLED],
        "letter": COUPLED,
        "pronunciation": PRONUNCIATION[EXAMPLE[COUPLED[0]]]
        # "image_link": IMAGE[COUPLED]

    }
    print(COUPLED)
    return jsonify(word_data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)