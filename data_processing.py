import zipfile
import pandas as pd
import json
import re

data = "./data/booksummaries.txt"

# txt 형식의 데이터를 json 형식으로 변경
def parse_line(line):
    fields = line.split('\t')
    fields = [field.replace("\\'", "'") for field in fields]  # 이스케이프 문자 처리
    fields[5] = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), fields[5])  # 유니코드 처리

    # 장르 부분 (예시: genres가 JSON 형태로 되어있다면 파싱)
    try:
        genres = json.loads(fields[5]) if fields[5].strip() else {}
    except json.JSONDecodeError:
        genres = {}

    result = {
        "WikiID": int(fields[0]),
        "title": fields[2],
        "author": fields[3],
        "publication_date": fields[4],
        "genres": genres,
        "summary": fields[6]
    }
    return result

with open(data, "r", encoding="utf-8") as file:
    parsed_lines = [parse_line(line.strip()) for line in file]

with open("book_summary.json", "w", encoding="utf-8") as json_file:
    json.dump(parsed_lines, json_file, indent=4, ensure_ascii=False)