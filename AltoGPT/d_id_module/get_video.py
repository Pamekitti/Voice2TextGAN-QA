import requests

d_id_api_key = "dGhha29ybi5zd2FAZ21haWwuY29t:0E_Y5JwuXCGu6HwiPgKhC"
url = "https://api.d-id.com/talks"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": "Basic " + d_id_api_key
}

response = requests.get("https://api.d-id.com/talks/tlk_MYWSFT9wU-ju7nkDUjzIW", headers=headers)
print(response.text)
