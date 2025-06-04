import torch
import librosa
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from transformers import AutoProcessor, AutoModelForCTC
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from transformers import logging
from itertools import groupby

# this script runs the transcription model. beware there are many dependencies.


# using facebook/wav2vec2-xlsr-53-espeak-cv-ft found at
# https://huggingface.co/facebook/wav2vec2-xlsr-53-espeak-cv-ft
def inference(audiopath: str, processor, model) -> str:
    audio, sr = librosa.load(audiopath, sr=16000)  # 16kHz is standard for wav2vec2
    input_values = processor(audio, return_tensors="pt").input_values

    with torch.no_grad():
        logits = model(input_values).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)

    return transcription[0]