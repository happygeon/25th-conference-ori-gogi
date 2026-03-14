"""서버 API 테스트 클라이언트"""
import os
import requests

SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

url = f"http://{SERVER_HOST}:{SERVER_PORT}/data"
response = requests.get(url)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}")