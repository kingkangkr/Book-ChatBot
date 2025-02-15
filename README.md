# Book-GPT (책-지피티)

- 소설 선택 시, 제목만으로는 소설의 줄거리나 분위기, 장르를 정확히 파악하기 어렵기 때문에 원하는 책을 찾기가 쉽지 않습니다.

- 이 프로젝트는 이러한 문제를 해결하기 위해 **LLM을 활용한 줄거리 기반의 소설 추천 시스템**을 개발하는 것을 목표로 합니다.

- 사용자가 소설 제목을 입력하면, AI가 해당 소설의 줄거리를 분석하고, 비슷한 내용의 소설을 추천하는 서비스를 제공합니다.


## Team

| 이름   | GitHub 프로필                           | 역할         |
|--------|--------------------------------------|--------------|
| 강병무 | [GitHub](https://github.com/kingkangkr) | 데이터 전처리, 프롬프트 작성 |
| 정희선 | [GitHub](https://github.com/lissani) | 데이터 크롤링, Streamlit UI 구현    |


##  프로젝트 구조
```bash
Book-GPT/
│── data/                    # 데이터셋 저장 폴더 (Hugging Face에서 다운로드 필요)
│── data_collecting/         # 외부 책 줄거리 크롤링
│── notebooks/               # 데이터 전처리 노트북 (Jupyter Notebook)
│── src/                     # 주요 Python 모듈
│   ├── data_loader.py       # 데이터 로드 기능
│   ├── recommender.py       # Faiss 기반 책 추천 기능
│   ├── chatbot.py           # OpenAI API를 사용한 설명 생성
│── main.py                  # Streamlit 애플리케이션 실행 파일
│── requirements.txt         # 프로젝트에서 필요한 패키지 목록
│── README.md                # 프로젝트 설명 문서
```

## 아키텍처 설계 도면
![image](https://github.com/user-attachments/assets/2b2d3b99-7a8b-485e-8ca1-f8f1d97d129c)

## 설치 및 실행 방법  

1. 저장소 클론
```bash
git clone https://github.com/your-username/Book-ChatBot.git
cd Book-ChatBot
```
2. 가상환경 생성
```bash
python -m venv myenv
source myenv/bin/activate  # Mac/Linux
myenv\Scripts\activate     # Windows
```
3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```
   
## 데이터 다운로드
이 프로젝트에서 사용하는 데이터는 Hugging Face에서 다운로드해야 합니다.
아래 명령어를 실행하여 data/ 폴더에 데이터를 다운로드하세요.
```bash
mkdir -p data  # Mac/Linux (폴더가 없을 경우 생성)
mkdir data     # Windows (폴더 생성)

wget -O data/filtered_booksummaries.csv "https://huggingface.co/datasets/kingkangkr/book_summary_dataset"
```
## 프로그램 실행
```bash
streamlit run main.py
```
##  환경 변수 설정 (.env 파일)
이 프로젝트는 OpenAI API를 사용하므로, API 키를 설정해야 합니다.
프로젝트 루트 디렉토리에 .env 파일을 만들고 아래 내용을 추가하세요.
```bash
OPENAI_API_KEY=your-api-key-here
```
## 결과
![Image](https://github.com/user-attachments/assets/e29346d3-c651-4ba1-9f6b-3f791db8e282)
