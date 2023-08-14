import pyaudio
import openai

from audio_stream import AudioStream

openai.api_key = "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"  # Eyp's key

# config to postprocess starting command
replace_alto = ["otto", "out", "ado", "all dough"]
replace_javis = ["chavis", "jowist", "john", "javith"]

# connect to microphone audio stream
stream = AudioStream(
    FRAMES_PER_BUFFER=4096, 
    FORMAT=pyaudio.paInt16, 
    CHANNELS=1, 
    RATE=44100,
    search_duration=5,
    command_duration=8
    )
audio_config = stream.get_config()

def transcribe_chunk(frames: list, language="en", audio_path='audio.wav'):
    AudioStream.create_chunk_wav(frames, audio_path, audio_config)
    audio_file = open(audio_path, "rb")
    return openai.Audio.transcribe("whisper-1", audio_file, language=language)

# whisper inference
print('start recording ...')
for idx, frames in iter(stream):
    print(idx)
    transcript = transcribe_chunk(frames, language="en")
    print("transcript: ", transcript)

    if idx >= 10:
        print("finish 10 batchs")
        break
