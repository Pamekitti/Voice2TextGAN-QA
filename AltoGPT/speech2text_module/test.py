import time
import pyaudio

from audio_stream import AudioStream
from alto_whisper import AltoWhisper

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

# class for inference whisper
alto_whisper = AltoWhisper(
    model_size="medium",
    audio_config = audio_config
    )

# whisper inference
print('start recording ...')
for idx, frames in iter(stream):
    # waiting for `Hey Alto`
    if not stream.active_status:
        result = alto_whisper.transcribe_chunk(frames, language="en")
        print('transcribe (wait): ', result)
    
        postprocess_result = result.lower().replace(',', '').replace('hello', 'hey')
        for name in replace_alto:
            postprocess_result = postprocess_result.replace(name, 'auto')
        for name in replace_javis:
            postprocess_result = postprocess_result.replace(name, 'javis')
    
        if any(command in postprocess_result for command in ['hey auto', 'hey javis', 'hey friday']):
            stream.active_status = True
            print('Hello, how can I assist you ?')
    
    # inference the command speech
    else:
        result = alto_whisper.transcribe_chunk(frames, language="en")
        print('transcribe (command): ', result)
        
        # reset the status to wait for another `Hey Alto`
        stream.active_status = False
