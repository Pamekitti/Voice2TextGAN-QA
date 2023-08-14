import requests

d_id_api_key = "dGhha29ybi5zd2FAZ21haWwuY29t:0E_Y5JwuXCGu6HwiPgKhC"
url = "https://api.d-id.com/tts/voices"

headers = {
    "accept": "application/json",
    "Authorization": "Basic " + d_id_api_key}

response = requests.get(url, headers=headers)

print(response.text)