import time
import pyaudio
import openai

# from alto_whisper import AltoWhisper
from audio_stream import AudioStream

openai.api_key = "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"  # Eyp's key


def run_recorder(hey_alto_pipe, answer_pipe, voice2text_queue):
    print('Starting recorder process...')

    # config to postprocess starting command
    replace_alto = ["otto", "out", "ado", "all dough"]
    replace_javis = ["chavis", "jowist", "john", "javith"]
    replace_elon = ['aaron']

    # connect to microphone audio stream
    stream = AudioStream(
        FRAMES_PER_BUFFER=4096,
        FORMAT=pyaudio.paInt16,
        CHANNELS=1,
        RATE=44100,
        search_duration=1,
        command_duration=5
    )
    audio_config = stream.get_config()
    
    def transcribe_chunk(frames: list, language="en", audio_path='audio.wav'):
        AudioStream.create_chunk_wav(frames, audio_path, audio_config)
        audio_file = open(audio_path, "rb")
        return openai.Audio.transcribe("whisper-1", audio_file, language=language)

    print('start recording ...')
    while True:
        # whisper inference
        for _, frames in iter(stream):
            # waiting for `Hey Alto`
            if not stream.active_status:
                result = transcribe_chunk(frames, language="en")
                print('transcribe (wait): ', result)
            
                postprocess_result = result.lower().replace(',', '').replace('hello', 'hey')
                for name in replace_alto:
                    postprocess_result = postprocess_result.replace(name, 'auto')
                for name in replace_javis:
                    postprocess_result = postprocess_result.replace(name, 'javis')
                for name in replace_elon:
                    postprocess_result = postprocess_result.replace(name, 'elon')

                # Keyword detected: Start inference the command speech
                if any(command in postprocess_result for command in ['hey auto', 'hey javis', 'hey friday', 'hey elon', 'hey', 'elon']):
                    stream.active_status = True
                    print('Hello, how can I assist you ?')

                    # Send the signal to the Video Generator to update "listening"
                    hey_alto_pipe.send('listening')

            # inference the command speech
            else:
                start = time.time()
                print('Transcribing question from audio...')
                result = transcribe_chunk(frames, language="en")
                print(f'Transcribing question from audio... DONE [Time taken: {time.time() - start:.1f} secs]')

                result = result.lower().replace('how can i help you', '').replace('?', '')
                print('transcribe (command): ', result)

                # Put result to the queue for QA model
                voice2text_queue.put(result)
                answer_pipe.recv()

                # reset the status to wait for another `Hey Alto`
                stream.active_status = False
