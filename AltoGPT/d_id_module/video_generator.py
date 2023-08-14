""" D-id API documentation:
https://docs.d-id.com/reference/get-started
"""

import time
import requests


D_ID_API_KEY = "dGhha29ybi5zd2FAZ21haWwuY29t:0E_Y5JwuXCGu6HwiPgKhC"  # Eyp's API key
person_image_url = "https://sustainability.pttgcgroup.com/storage/projects/circular-living-symposium/2022/speaker/speaker-11.jpg"

def generate_video(message: str, image_url: str, api_key: str, voice_id: str = "th-TH-NiwatNeural"):
    __voice_id__ = ["en-US-GuyNeural", "th-TH-NiwatNeural"]
    BASE_URL = "https://api.d-id.com"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Basic " + api_key
    }
    payload = {
        "script": {
            "type": "text",
            "input": str(message),
            "provider": {
                "type": "microsoft",
                "voice_id": str(voice_id)
            }
        },
        "source_url": image_url,
        "config": {
            "fluent": "false",
            "pad_audio": "0.0"
        }
    }

    response = requests.post(f"{BASE_URL}/talks", json=payload, headers=headers)
    print(response.text)
    if response.status_code != 201:
        return None

    video_id = response.json().get("id", "")
    for _ in range(5):
        _response = requests.get(f"{BASE_URL}/talks/{video_id}", headers=headers)
        video_response = _response.json()
        video_status = video_response.get("status", "")

        if video_status == "done":
            return video_response

        time.sleep(3)
        continue
    return None

input_message = "Climate change refers to the long-term alteration of Earth's average weather patterns and temperatures. It is primarily driven by human activities, such as burning fossil fuels (coal, oil, and natural gas) and deforestation, which release greenhouse gases into the atmosphere. These gases trap heat and lead to a warming effect known as the greenhouse effect. As a result, global temperatures rise, causing various impacts like melting ice, rising sea levels, more frequent and severe heatwaves, shifts in ecosystems, and disruptions to weather patterns. Climate change poses significant environmental, social, and economic challenges, making it crucial for nations to work together to reduce greenhouse gas emissions and adopt sustainable practices to mitigate its effects."
response:dict = generate_video(message=input_message,
                          image_url=person_image_url,
                          api_key=D_ID_API_KEY)

print(response)
