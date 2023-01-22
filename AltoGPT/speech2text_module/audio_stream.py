import pyaudio
import wave


class AudioStream:
    def __init__(self, FRAMES_PER_BUFFER=4096, FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=44100, search_duration=5, command_duration=8):
        self.FRAMES_PER_BUFFER = FRAMES_PER_BUFFER
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = RATE
        
        self.search_duration = search_duration
        self.command_duration = command_duration
        self.frames_in_second = int(RATE / FRAMES_PER_BUFFER * 1)

        self.p = pyaudio.PyAudio()
        self.sample_size = self.p.get_sample_size(self.FORMAT)

        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER
        )
        
        self.count = 0
        self.idx = 0
        self.frames = list()
        self.active_status = False  # enabled = speech command, disabled = waiting for `Hey Alto`
    
    def get_config(self):
        return {
            "FRAMES_PER_BUFFER": self.FRAMES_PER_BUFFER,
            "FORMAT": self.FORMAT,
            "CHANNELS": self.CHANNELS,
            "RATE": self.RATE,
            "sample_size": self.sample_size
        }
    
    def create_chunk_wav(frames: list, audio_path: str, audio_config: dict):
        wf = wave.open(str(audio_path), 'wb')
        wf.setnchannels(audio_config["CHANNELS"])
        wf.setsampwidth(audio_config["sample_size"])
        wf.setframerate(audio_config["RATE"])
        wf.writeframes(b''.join(frames))
        wf.close()

    def __iter__(self):
        self.count = -1
        return self
    
    def __next__(self):
        self.count += 1
        self.idx += 1

        # Stage 0: initial setup
        # if len(self.frames) == 0:
        #     print('listenting ...')
        #     for _ in range(self.frames_in_second*self.search_duration):
        #         data = self.stream.read(self.FRAMES_PER_BUFFER, exception_on_overflow=False)
        #         self.frames.append(data)

        # Stage 1: use sliding-window to find `Hey Alto` command
        if not self.active_status:
            print('listenting for start-command ...')
            self.frames = list()
            for _ in range(self.frames_in_second*self.search_duration):
                data = self.stream.read(self.FRAMES_PER_BUFFER, exception_on_overflow=False)
                self.frames.append(data)
            
            # for _ in range(self.frames_in_second):
            #     # remove 1-sec frames
            #     self.frames.pop(0)
            #     # append 1-sec frames
            #     data = self.stream.read(self.FRAMES_PER_BUFFER, exception_on_overflow=False)
            #     self.frames.append(data)

        # Stage 2: capture the whole speech of commands
        else:
            self.frames = list()
            print('listenting for commands ...')
            for _ in range(self.frames_in_second*self.command_duration):
                data = self.stream.read(self.FRAMES_PER_BUFFER, exception_on_overflow=False)
                self.frames.append(data)

        return self.idx, self.frames
