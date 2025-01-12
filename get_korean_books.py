import requests
from bs4 import BeautifulSoup

# 나무위키 URL
url = "https://namu.wiki/w/%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98%20%EB%B2%A0%EC%8A%A4%ED%8A%B8%EC%85%80%EB%9F%AC"

# 요청 헤더 설정 (User-Agent 추가 필요)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}

# HTTP 요청
response = requests.get(url, headers=headers)
response.raise_for_status()

# HTML 파싱
soup = BeautifulSoup(response.text, 'html.parser')
# irQanySx 클래스 안에 있는 Gv4yvdq 클래스의 title 속성 값 추출
titles = [
    a.get('title')
    for div in soup.find_all('div', class_='irQanySx')  # irQanySx 클래스 <div> 찾기
    for a in div.find_all('a', class_='+Gv4yvdq')  # 그 안의 <a> 태그 찾기
]

# 결과 출력
print(titles)