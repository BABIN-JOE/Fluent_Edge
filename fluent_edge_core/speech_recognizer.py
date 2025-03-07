import vosk
import json
from fluent_edge_core.audio_handler import audio_queue

# Load Vosk model
model = vosk.Model("model/vosk-model-en-us-0.22-lgraph")

# Function to transcribe audio
def transcribe_audio(full_transcription, stop_recording):
    rec = vosk.KaldiRecognizer(model, 16000)

    while not stop_recording.is_set():
        if not audio_queue.empty():
            data = audio_queue.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")

                if text:
                    full_transcription.append(text)
                    print(f"📝 Live: {text}")

    return " ".join(full_transcription)