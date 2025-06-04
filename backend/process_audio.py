import ffmpeg
import os
from transcribe.run import Runner

def convert_webm_to_wav(input_webm, output_wav):
    # Convert Opus audio to PCM format with mono (ac=1) or stereo (ac=2) using ffmpeg
    ffmpeg.input(input_webm).output(output_wav, acodec='pcm_s16le', ac=1, map='0:a', loglevel="quiet").run()

def process_raw_audio(runner: Runner, filename: str):
    # the filename : str argument does not include an extension!
    input_webm = f"./uploads/{filename}.webm"
    output_wav = f"./outputs/{filename}.wav"

    convert_webm_to_wav(input_webm, output_wav)
    transcriptions = runner.get_transcriptions_from_file(filename)

    os.remove(input_webm)
    with open(f"./outputs/{filename}.txt", mode="w", encoding="utf8") as text_output:
        text_output.write(str(transcriptions))

    return transcriptions

def process_file_audio(runner: Runner, filename: str):
    transcriptions = runner.get_transcriptions_from_file(filename)

    with open(f"./outputs/{filename}.txt", mode="w", encoding="utf8") as text_output:
        text_output.write(str(transcriptions))

    return transcriptions
    
