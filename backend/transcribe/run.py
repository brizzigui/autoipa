import torch
import librosa
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from transformers import AutoProcessor, AutoModelForCTC
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from transformers import logging
from itertools import groupby

# this script runs the transcription model. beware there are many dependencies.

class Runner:
    processor_xlsr = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-xlsr-53-espeak-cv-ft")
    model_xlsr = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-xlsr-53-espeak-cv-ft")

    processor_lv60 = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")
    model_lv60 = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")

    # using facebook/wav2vec2-xlsr-53-espeak-cv-ft found at
    # https://huggingface.co/facebook/wav2vec2-xlsr-53-espeak-cv-ft
    def facebook_wav2vec2_xlsr_53_espeak_cv_ft(self, audiopath: str) -> str:
        logging.set_verbosity_error()

        # Set up espeak for phonemizer
        EspeakWrapper.set_library("/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1")

        # Load the audio file (ensure the audio is at the sample rate the model expects, typically 16kHz)
        audio, sr = librosa.load(audiopath, sr=16000)  # 16kHz is standard for wav2vec2

        # Tokenize the audio (convert to input tensor)
        input_values = Runner.processor_xlsr(audio, return_tensors="pt").input_values

        # Retrieve logits from the model
        with torch.no_grad():
            logits = Runner.model_xlsr(input_values).logits

        # Take argmax and decode to get transcription
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = Runner.processor_xlsr.batch_decode(predicted_ids)

        return transcription[0]

    def facebook_wav2vec2_lv_60_espeak_cv_ft(self, audiopath: str) -> str:
        logging.set_verbosity_error()

        # Set up espeak for phonemizer
        EspeakWrapper.set_library("/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1")

        # Load the audio file (ensure the audio is at the sample rate the model expects, typically 16kHz)
        audio, sr = librosa.load(audiopath, sr=16000)  # 16kHz is standard for wav2vec2

        # Tokenize the audio (convert to input tensor)
        input_values = Runner.processor_lv60(audio, return_tensors="pt").input_values

        # Retrieve logits from the model
        with torch.no_grad():
            logits = Runner.model_lv60(input_values).logits

        # Take argmax and decode to get transcription
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = Runner.processor_lv60.batch_decode(predicted_ids)

        return transcription[0]


    def get_transcriptions_from_file(self, filename: str) -> dict[str, str]:
        audiopath = f"./outputs/{filename}.wav"
        
        transcriptions = {}
        transcriptions["facebook_wav2vec2_xlsr_53_espeak_cv_ft"] = self.facebook_wav2vec2_xlsr_53_espeak_cv_ft(audiopath)
        transcriptions["facebook_wav2vec2_lv_60_espeak_cv_ft"] = self.facebook_wav2vec2_lv_60_espeak_cv_ft(audiopath)

        print(transcriptions)
        return transcriptions