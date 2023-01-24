import time

from AltoGPT.qa_module.completions import answer_query_with_context
from AltoGPT.qa_module.embeddings import compute_doc_embeddings, preprocess_for_embeddings
import pickle
import requests
import io
import os
from config import api
from concurrent.futures import ThreadPoolExecutor
from moviepy.editor import VideoFileClip, concatenate_videoclips

os.environ['EXHUMAN_API_KEY'] = api.exh_api_key

df = preprocess_for_embeddings()
embedding_path = 'AltoGPT/assets/embedded-data/document_embeddings.pickle'
EMBEDDING_REQUIRED = False
if EMBEDDING_REQUIRED:
    # Compute document embeddings
    print('Computing document embeddings...')
    document_embeddings = compute_doc_embeddings(df)
    # Save document embeddings
    with open(embedding_path, 'wb') as handle:
        pickle.dump(document_embeddings, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print('Document embeddings saved to', embedding_path)

else:
    with open(embedding_path, 'rb') as handle:
        document_embeddings = pickle.load(handle)

BOT_NAME = {
    "Elon Musk": "Marc",
    "Cinderella": "Fiona"
}

headers = {"Authorization": f"Bearer {os.environ['EXHUMAN_API_KEY']}"}
bot_name = "Elon Musk"
api_endpoint = api.exh_api_endpoint


def split_text_into_sentences(text):
    UPPERBOUND_SENTENCE_LENGTH = 100

    if len(text.split(".")[:-1]) == 0:
        main_sentences = [text]
    else:
        main_sentences = text.split(".")[:-1]

    result = list()
    for sentence in main_sentences:

        # Preprocess sentence
        sentence = sentence.replace('"', '')

        if len(sentence) > UPPERBOUND_SENTENCE_LENGTH:
            sub_sentences = sentence.split(",")

            # Keep track of the length of the sub_sentences
            sum_sub_sentence_length = 0
            sub_s = list()

            for sub_sentence in sub_sentences:
                if len(sub_sentence) > UPPERBOUND_SENTENCE_LENGTH:
                    word_lists = sub_sentence.strip().split(" ")

                    # Keep track of the length of the words
                    sum_word_length = 0
                    words = list()

                    # For sub_sentence which is still too long, split into words
                    for word in word_lists:

                        if sum_word_length > UPPERBOUND_SENTENCE_LENGTH:
                            result.append(" ".join(words))
                            words = list()
                            sum_word_length = 0
                        else:
                            words.append(word)
                            sum_word_length += len(word) + 1

                    if len(words) > 0:  # If there are words left over, append them
                        result.append(" ".join(words))

                else:  # If sub_sentence is not too long, append it

                    if sum_sub_sentence_length > UPPERBOUND_SENTENCE_LENGTH:
                        result.append(" ".join(sub_s))
                        sum_sub_sentence_length = 0
                        sub_s = list()
                    else:
                        sub_s.append(sub_sentence)
                        sum_sub_sentence_length += len(sub_sentence) + 1

            if len(sub_s) > 0:  # If there are sub-sentences left over, append them
                result.append(" ".join(sub_s))

        else:  # If sentence is not too long, append it
            result.append(sentence.strip())

    return result


def get_video_from_exhuman_api(input):
    index, text = input
    body = {
        'bot_name': bot_name,
        'bot_response': text,
        'voice_name': BOT_NAME[bot_name]
    }

    while True:
        time.sleep(0.5)
        res = requests.post(api_endpoint, json=body, headers=headers)
        if b'message' not in res.content:
            print(f"[{index}] Successfully generated video")
            break

    video_byte = io.BytesIO(res.content)

    file_name = f"AltoGPT/assets/bot-videos/tempfile{index}.mp4"

    if os.path.exists(file_name):
        os.remove(file_name)
    with open(file_name, "wb") as f:
        print(f"Writing video {file_name} to file")
        f.write(video_byte.read())

    return VideoFileClip(file_name)


def generate_video_from_text(text):

    # Preprocess text
    text = text.replace('"', '')
    text = text.replace('&', 'and')

    # Break text in to sentences with a max length of 155 characters
    sentences = split_text_into_sentences(text)
    print(sentences)

    inputs = [(i, sentence) for i, sentence in enumerate(sentences)]
    print(f"There are {len(inputs)} sentences...")
    with ThreadPoolExecutor() as executor:
        output_videos = executor.map(get_video_from_exhuman_api, inputs)

    # Concatenate all the videos and save as a single video
    time.sleep(0.5)
    final_video = concatenate_videoclips(list(output_videos))
    final_video.write_videofile("AltoGPT/assets/bot-videos/final_video.mp4")
    for vdo in output_videos:
        vdo.close()

    # Extract audio from the video
    final_video = VideoFileClip("AltoGPT/assets/bot-videos/final_video.mp4")
    final_video.audio.write_audiofile("AltoGPT/assets/bot-videos/final_video.mp3")
    final_video.close()


def generate_answer(voice2text_queue, qa_parent):
    print('Starting QA process...')

    while True:

        try:
            query = voice2text_queue.get()
            print(f'Got the answer from Q process... {query}')

            start = time.time()
            print('Generating answer...')
            response = answer_query_with_context(query, df, document_embeddings, diag=False)
            print(f'Generating answer... DONE [Time taken: {time.time() - start:.1f} secs]')

            print(f"\nQ: {query}\nA: {response}")

            start = time.time()
            print('Generating video from text...')
            generate_video_from_text(response)
            print(f'Generating video from text... DONE [Time taken: {time.time() - start:.1f} secs]')

            print('Sent the answer to QA Queue process, Current Queue Size: ', voice2text_queue.qsize())
            qa_parent.send('success')
        except Exception as e:
            print(f"Error in QA process: {e}")
            qa_parent.send('fail')
