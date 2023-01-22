from AltoGPT.completions import answer_query_with_context
from AltoGPT.embeddings import compute_doc_embeddings, preprocess_for_embeddings
import pickle
import requests
import io
import os
import cv2
import subprocess, sys

os.environ['EXHUMAN_API_KEY'] = "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VybmFtZSI6ImFuZGFtYW4ubGVrYXdhdEBnbWFpbC5jb20ifQ.xpW2ZnkPx5Scd9V5lgt-uAXSCmWcMxwEVpf8ZPC9NxstClM0UzrcX-6OlMW7fwke0Prt3aSMMd7fzVaqF8wlwA"

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
api_endpoint = "https://api.exh.ai/animations/v1/generate_lipsync"
video_path = "AltoGPT/assets/bot-videos/tempfile.mp4"

"""
the Completions API is used to answer the user's query.
"""


def post_to_exh(text):
    body = {
        'bot_name': bot_name,
        'bot_response': text,
        'voice_name': BOT_NAME[bot_name]
    }
    res = requests.post(api_endpoint, json=body, headers=headers)
    return io.BytesIO(res.content)


if __name__ == "__main__":
    query = ''
    while True:
        query = input('\nEnter your Answer: ')
        if query == 'exit':
            break
        else:
            answer = answer_query_with_context(query, df, document_embeddings, diag=False)
            print(f"\nQ: {query}\nA: {answer}")

            # break answer in to sentences
            if len(answer) >= 150:
                answer = answer.split('.')
                # drop last one
                answer = answer[:-1]
            vid_num = len(answer)
            streams = []
            for sentence in answer:
                # if sentence length is longer than 150 characters, break it in to smaller sentences
                if len(sentence) >= 150:
                    ss = sentence.split(',')
                    for s in ss:
                        response_stream = post_to_exh(s)
                        streams.append(response_stream)
                else:
                    response_stream = post_to_exh(sentence)
                    streams.append(response_stream)

            for i, stream in enumerate(streams):
                with open(f"AltoGPT/assets/bot-videos/tempfile{i}.mp4", "wb") as f:
                    f.write(stream.read())

        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener,  video_path])