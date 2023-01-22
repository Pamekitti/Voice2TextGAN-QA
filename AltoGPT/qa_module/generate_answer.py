from AltoGPT.qa_module.completions import answer_query_with_context
from AltoGPT.qa_module.embeddings import compute_doc_embeddings, preprocess_for_embeddings
import pickle
import requests
import io
import os
from config import api
from moviepy.editor import VideoFileClip, concatenate_videoclips

os.environ['EXHUMAN_API_KEY'] = api.exh_api_key

df = preprocess_for_embeddings()
embedding_path = 'AltoGPT/assets/embedded-data/document_embeddings.pickle'
EMBEDDING_REQUIRED = False
if EMBEDDING_REQUIRED:
    # Compute document embeddings
    document_embeddings = compute_doc_embeddings(df)
    # Save document embeddings
    with open(embedding_path, 'wb') as handle:
        pickle.dump(document_embeddings, handle, protocol=pickle.HIGHEST_PROTOCOL)

else:
    with open(embedding_path, 'rb') as handle:
        document_embeddings = pickle.load(handle)

BOT_NAME = {
    "Elon Musk": "Max",
    "Cinderella": "Fiona"
}

headers = {"Authorization": f"Bearer {os.environ['EXHUMAN_API_KEY']}"}
bot_name = "Cinderella"
api_endpoint = api.exh_api_endpoint


def post_to_exh(text):
    body = {
        'bot_name': bot_name,
        'bot_response': text,
        'voice_name': BOT_NAME[bot_name]
    }
    res = requests.post(api_endpoint, json=body, headers=headers)
    return io.BytesIO(res.content)


def generate_video_from_text(text):
    # break text in to sentences
    if len(text) >= 150:
        text = text.split('.')
        # drop last one
        text = text[:-1]
    else:
        text = [text]
    streams = []
    print(text)
    for sentence in text:
        # if sentence length is longer than 150 characters, break it in to smaller sentences
        if len(sentence) >= 150:
            ss = sentence.split(',')
            for s in ss:
                response_stream = post_to_exh(s)
                streams.append(response_stream)
        else:
            response_stream = post_to_exh(sentence)
            streams.append(response_stream)

    video_obj_list = list()
    for i, stream in enumerate(streams):
        file_name = f"AltoGPT/assets/bot-videos/tempfile{i}.mp4"
        with open(file_name, "wb") as f:
            print(f"Writing video {i} to file")
            f.write(stream.read())
            video_obj_list.append(VideoFileClip(file_name))

    final_video = concatenate_videoclips(video_obj_list)
    final_video.write_videofile("AltoGPT/assets/bot-videos/final_video.mp4")


def generate_answer_video_from_question(question):
    answer = answer_query_with_context(question, df, document_embeddings, diag=False)
    print(f"\nQ: {question}\nA: {answer}")
    generate_video_from_text(answer)


if __name__ == "__main__":
    query = ''
    while True:
        query = input('\nEnter your Answer: ')
        if query == 'exit':
            break
        else:
            response = answer_query_with_context(query, df, document_embeddings, diag=False)
            print(f"\nQ: {query}\nA: {response}")
            generate_video_from_text(response)
