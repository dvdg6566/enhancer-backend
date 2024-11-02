import base64
import speech_recognition as sr
import soundfile as sf
import io as io
import wave
import subprocess
from time import time

def process_audofile(audio_string):

    init = time()

    audio_string = f.read()
    audio_string = audio_string.replace('\n','')

    print(len(audio_string))
    webm_filename = "output.webm"
    wav_filename = "output.wav"

    subprocess.run(f"rm {wav_filename}", shell=True)
    r = sr.Recognizer()

    with open(webm_filename, "wb") as f:
        decoded_string = base64.b64decode(audio_string)
        f.write(decoded_string)

    print(f"Converting file: {time() - init}")

    command = f"ffmpeg -i {webm_filename} -vn -acodec pcm_s16le -ar 44100 -ac 2 {wav_filename}"
    subprocess.run(command, shell=True)

    print(f"Converted file: {time() - init}")

    with sr.AudioFile(wav_filename) as source:
        # Listen for the data (load audio to memory)
        audio_data = r.record(source)

    text = r.recognize_google(audio_data)  
    print("Transcription: ", text)

    print(f"Transcribed: {time() - init}")