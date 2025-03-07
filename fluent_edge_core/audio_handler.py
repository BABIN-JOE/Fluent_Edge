import sounddevice as sd
import queue
import sys

# Queue for storing audio data
audio_queue = queue.Queue()

# Callback function to capture audio data
def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))

# Function to start audio recording
def start_recording():
    try:
        stream = sd.RawInputStream(
            samplerate=16000,
            blocksize=4000,
            dtype='int16',
            channels=1,
            callback=audio_callback
        )
        stream.start()
        return stream
    except Exception as e:
        print(f"❌ ERROR: Failed to start audio recording. {e}")
        return None

# Function to stop audio recording
def stop_recording(stream):
    if stream:
        stream.stop()
        stream.close()