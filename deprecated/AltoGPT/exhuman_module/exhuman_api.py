import io
import os
import time
import asyncio
import requests
import aiohttp
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip


class ExHumanAI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.url = "https://api.exh.ai/animations/v3/generate_lipsync"
        self.idle_video_url = "https://ugc-idle.s3-us-west-2.amazonaws.com/est_5e0f92b8c77a209b54710019730ff9c9.mp4"

        # Download the idle video
        idle_video_content = requests.get(self.idle_video_url).content

        # Save the idle video
        os.makedirs('temp', exist_ok=True)
        if os.path.exists('temp/idle.mp4'):
            os.remove('temp/idle.mp4')

        with open('temp/idle.mp4', 'wb') as f:
            f.write(idle_video_content)

        print("Idle video downloaded")

    async def get_clip_async(self, session, text):
        """ Generate a clip asynchronously
        Args:
            session (aiohttp.ClientSession): Client session
            text (str): Text to generate
        Returns:
            bytes: Video content
        """
        url = self.url
        payload = {
            "text": text,
            "idle_url": self.idle_video_url,
            "voice_name": "Elon"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_token}"
        }

        async with session.post(url, json=payload, headers=headers) as response:
            return await response.read()

    def generate_video(self, text):
        asyncio.run(self.generate_video_async(text))

    async def generate_video_async(self, text):
        """ Generate a video from text asynchronously
        Args:
            text (str): Text to generate
        """
        sentences = self._preprocess_text(text)
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_clip_async(session, sentence) for sentence in sentences]
            responses = await asyncio.gather(*tasks)

        clips = []
        for i, content in enumerate(responses):
            _start = time.time()
            video_byte = io.BytesIO(content)
            file_name = f"temp/video{i}.mp4"

            if os.path.exists(file_name):
                os.remove(file_name)
            with open(file_name, "wb") as f:
                print(f"Writing video {file_name} to file")
                f.write(video_byte.read())
            clips.append(VideoFileClip(file_name))
            print(f"Time taken to write video {file_name}: {time.time() - _start} seconds")

        _start = time.time()
        final = concatenate_videoclips(clips)
        final.write_videofile("temp/final.mp4")
        for clip in clips:
            clip.close()
        print(f"Time taken to concatenate videos: {time.time() - _start} seconds")

    def _preprocess_text(self, text):
        """ Preprocess text to fit ExHuman API requirements
        The text should not exceed 200 characters.

        If the text exceeds 200 characters, split the text into sentences and return a list of sentences.

        Args:
            text (str): Text to preprocess

        Returns:
            list[str]: Preprocessed text

        """
        final_sentences = ['']

        if len(text) < 200:
            return [text]
        else:
            sentences = [s for s in text.split('.') if s]

            for each_sentence in sentences:
                if len(final_sentences[-1]) + len(each_sentence) < 200:
                    final_sentences[-1] += f". {each_sentence}"
                elif len(each_sentence) < 200:
                    final_sentences.append(each_sentence)
                else:  # If the sentence is still too long

                    words = each_sentence.split(' ')
                    final_sentences.append('')

                    for each_word in words:
                        if len(final_sentences[-1]) + len(each_word) < 200:
                            final_sentences[-1] += f" {each_word}"
                        else:
                            final_sentences.append(each_word)

            return [s for s in final_sentences if s]


if __name__ == "__main__":
    api_token = ""
    video_generator = ExHumanAI(api_token)
    start = time.time()
    text = "Alto CERO is a product line developed by AltoTech Global, focusing on sustainability and energy management. It uses advanced technologies like AI, machine learning, and IoT to optimize energy use and enhance user comfort in various settings."
    video_generator.generate_video(text)
    print(f"Time taken: {time.time() - start} seconds")
