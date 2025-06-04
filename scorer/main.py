from wsgiref.util import request_uri
from datasets import load_dataset, Audio
import librosa
import soundfile as sf
import jiwer
import os
from typing import cast
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from transformers import logging
from run import inference

def clean(original: str) -> str:
    for symbol in ["ˌ", ",", "ˈ", "'"]:
        original = original.replace(symbol, "")

    return original

# calculates the phoneme error rate, akin to the char error rate used commonly in asr
# https://huggingface.co/learn/audio-course/en/chapter5/evaluation
def compare(predicted: str, reference: str) -> float:
    result = jiwer.cer(reference, predicted)
    return cast(float, result)

def prepare() -> tuple:
    logging.set_verbosity_error()
    EspeakWrapper.set_library('C:\\Program Files\\eSpeak NG\\libespeak-ng.dll')

    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-xlsr-53-espeak-cv-ft")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-xlsr-53-espeak-cv-ft")
    xlsr_53 = (processor, model)

    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")
    lv_60 = (processor, model)

    return (xlsr_53, lv_60)

def clear_output() -> None:
    file_full = open("./scorer/results/full.csv", "w", encoding="utf8")
    file_short = open("./scorer/results/short.csv", "w", encoding="utf8")
    file_full.close()
    file_short.close()

def load():
    dataset = load_dataset("bookbot/ljspeech_phonemes", split="train")
    dataset = dataset.cast_column("audio", Audio())
    return dataset

def show_progress(index, size) -> None:
    print(f"\r[{"-"*int(25*index/size)}{"."*int(25*(1-index/size))}] = {100*index/size:.2f}% done, ran {index} samples      ", end="",flush=True)


def main() -> None:
    xlsr_53, lv_60 = prepare()
    clear_output()
    dataset = load()

    sum_cer_xlsr_53 = 0
    sum_cer_lv_60 = 0
    size = len(dataset)
    iter = 0

    for index, example in enumerate(dataset):
        # extracts fields
        audio = example["audio"]
        raw_audio = audio["array"]
        original_sr = audio["sampling_rate"]

        # saves resampled to file
        resampled_array = librosa.resample(raw_audio, orig_sr=original_sr, target_sr=16000)
        sf.write("./scorer/tmp/audio.wav", resampled_array, 16000)

        # removes stress marks and spaces
        predicted_xlsr_53 = inference("./scorer/tmp/audio.wav", xlsr_53[0], xlsr_53[1]).replace(" ", "").replace("ː", "")
        predicted_lv_60 = inference("./scorer/tmp/audio.wav", lv_60[0], lv_60[1]).replace(" ", "").replace("ː", "")
        reference = clean(example["phonemes"]).replace(" ", "")

        # compares and updated
        cer_xlsr_53 = compare(predicted_xlsr_53, reference)
        cer_lv_60 = compare(predicted_lv_60, reference)
        sum_cer_xlsr_53 += cer_xlsr_53
        sum_cer_lv_60 += cer_lv_60
        iter += 1

        # writes to file
        with open("./scorer/results/full.csv", "a", encoding="utf8") as file_full:
            file_full.write(f"{index},{len(reference)},{len(predicted_xlsr_53)},{len(predicted_lv_60)},{cer_xlsr_53},{cer_lv_60},{predicted_xlsr_53},{predicted_lv_60},{reference}\n")

        show_progress(index, size)
        os.remove("./scorer/tmp/audio.wav")

    avg_cer_xlsr_53 = sum_cer_xlsr_53 / iter
    avg_cer_lv_60 = sum_cer_lv_60 / iter

    with open("./scorer/results/short.csv", "w", encoding="utf8") as file_short:
        file_short.write(f"Average char error rate for xlsr_53: {avg_cer_xlsr_53}\n")
        file_short.write(f"Average char error rate for lv_60: {avg_cer_lv_60}\n")

if __name__ == "__main__":
    main()