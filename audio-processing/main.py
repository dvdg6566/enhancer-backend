import base64
import speech_recognition as sr
import soundfile as sf
import io as io
import wave
import subprocess

with open("test_audio", "r") as f:
    audio_string = f.read()

print(len(audio_string))
webm_filename = "output.webm"
wav_filename = "output.wav"
r = sr.Recognizer()

with open(webm_filename, "wb") as f:
    decoded_string = base64.b64decode(audio_string)
    f.write(decoded_string)

command = f"ffmpeg -i {webm_filename} -vn -acodec pcm_s16le -ar 44100 -ac 2 {wav_filename}"
subprocess.run(command, shell=True)

with sr.AudioFile(wav_filename) as source:
    # Listen for the data (load audio to memory)
    audio_data = r.record(source)

text = r.recognize_google(audio_data)  
print("Transcription: ", text)