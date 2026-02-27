from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil, os
from processor import process_files

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def validate_file(file: UploadFile, allowed_extensions: list, allowed_types: list):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension. Allowed: {allowed_extensions}"
        )
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {allowed_types}"
        )


@app.post("/upload")
async def upload_files(
    pdf_file: UploadFile = File(...),
    co2_file: UploadFile = File(...)
):
    validate_file(
        pdf_file,
        allowed_extensions=[".pdf"],
        allowed_types=["application/pdf"]
    )
    validate_file(
        co2_file,
        allowed_extensions=[".xlsx"],
        allowed_types=["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
    )

    pdf_path = os.path.join(UPLOAD_DIR, pdf_file.filename)
    co2_path = os.path.join(UPLOAD_DIR, co2_file.filename)

    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)

    with open(co2_path, "wb") as f:
        shutil.copyfileobj(co2_file.file, f)

    output_file = process_files(pdf_path, co2_path)
    filename = os.path.basename(output_file)

    return {"filename": filename}


@app.get("/download/{filename}")
def download_file(filename: str):
    filename = os.path.basename(filename)
    file_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )
