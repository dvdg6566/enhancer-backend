import base64
import speech_recognition as sr
import io as io
import wave
import subprocess
from time import time
from termcolor import cprint

def process_audiofile(audio_string):

    init = time()

    audio_string = audio_string.replace('\n','')
    audio_string = ''.join(audio_string.split('base64,')[1:]) # Removes prefix

    # with open("test_audio", "r") as f:
    #     f.write(audio_string)

    webm_filename = "output.webm"
    wav_filename = "output.wav"

    subprocess.run(f"rm {wav_filename}", shell=True)
    r = sr.Recognizer()

    with open(webm_filename, "wb") as f:
        decoded_string = base64.b64decode(audio_string)
        f.write(decoded_string)

    command = f"ffmpeg -i {webm_filename} -vn -acodec pcm_s16le -ar 44100 -ac 2 {wav_filename}"
    s = subprocess.run(command, shell=True, capture_output=True)

    if  "Invalid data" in s.stderr.decode():
        cprint("ffmpeg failed, autofile invalid!", "red")
        return ''

    with sr.AudioFile(wav_filename) as source:
        # Listen for the data (load audio to memory)
        audio_data = r.record(source)

    try:
        text = r.recognize_google(audio_data)  
    except:
        cprint("Speech recognition error", "yellow")
        return ""

    print("Transcription: ", text)
    print(f"Transcribed: {time() - init}")
    return text

if __name__ == '__main__':
    with open("test_audio", "r") as f:
        audio_string = f.read()

    process_audiofile(audio_string)
