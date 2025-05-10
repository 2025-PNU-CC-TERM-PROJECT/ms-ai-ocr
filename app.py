from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import easyocr
import tempfile
import shutil
import re

app = FastAPI()
reader = easyocr.Reader(['en', 'ko'])  # 영어 + 한글 지원

#  텍스트에서 상호명, 날짜, 총액 추출
def extract_info(lines):
    store = next((line for line in lines if "점" in line or "편의점" in line or "마트" in line), None)
    date_line = next((line for line in lines if re.search(r'\d{4}[./-]\d{1,2}[./-]\d{1,2}', line)), None)
    total_line = next((line for line in lines if re.search(r'(합계|총액|총\s*금액).*?\d+', line)), None)

    # 날짜 포맷 정리
    date = None
    if date_line:
        match = re.search(r'\d{4}[./-]\d{1,2}[./-]\d{1,2}', date_line)
        if match:
            date = match.group().replace('.', '-').replace('/', '-')

    # 총액 숫자만 추출
    total = None
    if total_line:
        numbers = re.findall(r'\d{3,}', total_line)
        if numbers:
            total = numbers[-1]

    return {
        "store": store or "Unknown",
        "date": date or "Unknown",
        "total": total or "Unknown",
        "lines": lines  # 원문도 같이 반환
    }

@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        results = reader.readtext(tmp_path)
        lines = [res[1] for res in results]

        extracted = extract_info(lines)
        return JSONResponse(content=extracted)

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # 로그로 확인
        return JSONResponse(status_code=500, content={"error": str(e)})

