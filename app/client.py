import requests

# 서버의 IP 주소와 포트를 설정합니다.
server_ip = "192.168.219.107"  # 서버의 IP 주소로 설정합니다.
port = 8000

# API 엔드포인트 URL을 설정합니다.
url = f"http://{server_ip}:{port}/data"

# GET 요청을 보냅니다.
response = requests.get(url)

# 응답이 성공적인지 확인합니다.
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}")