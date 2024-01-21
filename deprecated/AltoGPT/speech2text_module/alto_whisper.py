import os
import whisper

from audio_stream import AudioStream


class AltoWhisper:
    __model_size__ = ["tiny", "base", "small", "medium", "large"]
    
    def __init__(self, model_size: str, audio_config: dict):
        self.model_size = model_size
        self.model = self.load_model(self.model_size)
        self.audio_config = audio_config\

        self.model = self.model.cuda()
    
    def load_model(self, model_size):
        model_path = f"checkpoints/{model_size}.pt"
        
        if not os.path.exists(model_path):
            model = whisper.load_model(
                name=str(model_size),
                download_root="checkpoints",
                in_memory=True
                )
        else:
            model = whisper.load_model(
                name=f"checkpoints/{model_size}.pt",
                download_root="checkpoints",
                in_memory=True
                )

        return model
    
    def transcribe_file(self, audio_path, language="en"):
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)

        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        options = whisper.DecodingOptions(
            task="transcribe",
            language=language,
            fp16=True)
        result = whisper.decode(self.model, mel, options)
        return result.text

    def transcribe_chunk(self, frames: list, language="en", audio_path='audio.wav'):
        AudioStream.create_chunk_wav(frames, audio_path, self.audio_config)
        return self.transcribe_file(audio_path, language)
