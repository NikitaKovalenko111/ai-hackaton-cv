import asyncio
import io
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel, field_serializer
from typing import List
from ultralytics import YOLO

from model.classificator.classificator import create_dataset_csv, train_classificator, prepare_data
from model.train import train_model
from model.utils.model_math import getPpc
from utils.model_math import measure_objects, calculate_ppc_from_chessboard
from utils.preprocessing import auto_orient
from dotenv import load_dotenv

app = FastAPI(title="YOLO Detection API")

load_dotenv('.env')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # FIXME
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

WEIGHTS_PATH = BASE_DIR / "runs" / "segment" / "plant_seg_v22" / "weights" / "best.pt"
DATASET_PATH = BASE_DIR / "dataset"
DATASET_MEASURMENTS_PATH = BASE_DIR / "classificator" / "dataset_measurements.csv"

if not WEIGHTS_PATH.exists():
    raise FileNotFoundError(f"Модель не найдена по пути: {WEIGHTS_PATH}")

print(f"Загрузка модели из: {WEIGHTS_PATH}")

model = YOLO(str(WEIGHTS_PATH))

create_dataset_csv(DATASET_PATH, model_path=WEIGHTS_PATH, pixels_per_cm=getPpc(), output_csv=DATASET_MEASURMENTS_PATH)

classificator = train_classificator(DATASET_MEASURMENTS_PATH)

print("Модель загружена!")

class DetectionBox(BaseModel):
    class_name: str
    length_px: float
    length_cm: float
    confidence: float
    area_px: float
    area_cm: float

    @field_serializer('length_px', 'length_cm', 'confidence')
    def round_floats(self, value: float) -> float:
        if value is None:
            return None
        return round(value, 2)


class PredictionResponse(BaseModel):
    image_width: int
    image_height: int
    image_base64: str
    type: str
    detections: List[DetectionBox]

@app.post("/predict", response_model=PredictionResponse)
async def predict(files: List[UploadFile] = File(...)):
    response = []

    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Файл должен быть изображением")

        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert("RGB")

            pixels_per_cm = getPpc()
            width = image.width
            height = image.height

            img = auto_orient(image)
            results = await asyncio.to_thread(model.predict, img, conf=0.3, save=True, imgsz=640)
            measurements, jpg_bytes = measure_objects(results)
            x = prepare_data(measurements, pixels_per_cm)
            pred = await asyncio.to_thread(classificator.predict, x)
            detections = []

            for m in measurements:

                print(
                    f"{m['class']}: {m['length_px']:.1f} px, {m['length_px'] / pixels_per_cm} cm (conf: {m['confidence']:.2f})")
                detections.append(DetectionBox(
                    class_name=m['class'],
                    length_px=m['length_px'],
                    length_cm=m['length_px'] / pixels_per_cm,
                    confidence=m['confidence'],
                    area_px=m['area_px'],
                    area_cm= m['area_px'] / (pixels_per_cm**2),
                ))
                if pred[0]:
                    type = "Пшеница"
                else:
                    type = "Руккола"

            response.append(PredictionResponse(
                image_width=width,
                image_height=height,
                image_base64=jpg_bytes,
                type=type,
                detections=detections,
            ))

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return response

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)