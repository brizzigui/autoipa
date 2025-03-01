import ffmpeg
import os
from transcribe.run import get_transcription_from_file

def convert_webm_to_wav(input_webm, output_wav):
    os.remove(output_wav)
    # Convert Opus audio to PCM format with mono (ac=1) or stereo (ac=2)
    ffmpeg.input(input_webm).output(output_wav, acodec='pcm_s16le', ac=1, map='0:a').run()

def process_audio():
    input_webm = "./uploads/recording.webm"
    output_wav = "./outputs/recording.wav"

    convert_webm_to_wav(input_webm, output_wav)
    return get_transcription_from_file()
    
