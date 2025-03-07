import sounddevice as sd
import numpy as np

def test_audio():
    duration = 5  # seconds
    samplerate = 16000
    print("Recording... Speak now!")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    print("Recording complete!")
    return audio

audio_data = test_audio()
print("Audio captured:", np.any(audio_data))
