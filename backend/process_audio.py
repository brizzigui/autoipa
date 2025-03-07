import ffmpeg
import os
from transcribe.run import get_transcription_from_file

def convert_webm_to_wav(input_webm, output_wav):
    # Convert Opus audio to PCM format with mono (ac=1) or stereo (ac=2) using ffmpeg
    ffmpeg.input(input_webm).output(output_wav, acodec='pcm_s16le', ac=1, map='0:a', loglevel="quiet").run()

def process_audio(filename: str):
    # the filename : str argument does not include an extension!
    input_webm = f"./uploads/{filename}.webm"
    output_wav = f"./outputs/{filename}.wav"

    convert_webm_to_wav(input_webm, output_wav)
    transcription = get_transcription_from_file(filename)

    os.remove(input_webm)
    with open(f"./outputs/{filename}.txt", mode="w", encoding="utf8") as text_output:
        text_output.write(transcription[0])

    return transcription[0]
    
