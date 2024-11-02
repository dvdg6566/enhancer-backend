import base64

with open("test_audio", "r") as f:
    audio_string = f.read()

with open("output.wav", "wb") as f:
    f.write(base64.b64decode(audio_string))
