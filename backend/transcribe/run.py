import torch
import librosa
from transformers import AutoProcessor, AutoModelForCTC
from phonemizer.backend.espeak.wrapper import EspeakWrapper

# using facebook/wav2vec2-lv-60-espeak-cv-ft
# https://huggingface.co/facebook/wav2vec2-lv-60-espeak-cv-ft

def get_transcription_from_file() -> str:
    # Set up espeak for phonemizer
    EspeakWrapper.set_library('C:\Program Files\eSpeak NG\libespeak-ng.dll')

    # Load the processor and model
    processor = AutoProcessor.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")
    model = AutoModelForCTC.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")

    # Load your own audio file (replace 'path_to_your_audio.wav' with the actual path to your file)
    audio_path = './outputs/recording.wav'

    # Load the audio file (ensure the audio is at the sample rate the model expects, typically 16kHz)
    audio, sr = librosa.load(audio_path, sr=16000)  # 16kHz is standard for wav2vec2

    # Tokenize the audio (convert to input tensor)
    input_values = processor(audio, return_tensors="pt").input_values

    # Retrieve logits from the model
    with torch.no_grad():
        logits = model(input_values).logits

    # Take argmax and decode to get transcription
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)

    # Print the transcription
    print(transcription)
    return transcription