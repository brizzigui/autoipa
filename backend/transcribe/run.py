import torch
import librosa
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from transformers import logging

# this script runs the transcription model. beware there are many dependencies.

# using facebook/wav2vec2-xlsr-53-espeak-cv-ft found at
# https://huggingface.co/facebook/wav2vec2-xlsr-53-espeak-cv-ft
# before, i was using facebook/wav2vec2-lv-60-espeak-cv-ft found at
# https://huggingface.co/facebook/wav2vec2-lv-60-espeak-cv-ft

def get_transcription_from_file(filename: str) -> str:
    logging.set_verbosity_error()

    # Set up espeak for phonemizer
    EspeakWrapper.set_library('C:\Program Files\eSpeak NG\libespeak-ng.dll')

    # Load the processor and model
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-xlsr-53-espeak-cv-ft")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-xlsr-53-espeak-cv-ft")

    # Load your audio file
    audio_path = f'./outputs/{filename}.wav'

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