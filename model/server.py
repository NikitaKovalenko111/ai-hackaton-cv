import asyncio
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
from typing import List
from ultralytics import YOLO
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

print("Загрузка модели YOLO...")
model = YOLO('model/runs/segment/plant_seg_v1/weights/best.pt')
print("Модель загружена!")

class DetectionBox(BaseModel):
    class_name: str
    length_px: float
    length_cm: float
    confidence: float


class PredictionResponse(BaseModel):
    image_width: int
    image_height: int
    image_base64: str
    detections: List[DetectionBox]

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    try:

        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        pixels_per_cm = calculate_ppc_from_chessboard(
            'model/dataset/calibrate/calib_10.jpg',
            chessboard_size=(4, 7),
            square_size_cm=1.0
        )

        img = auto_orient(image)
        results = await asyncio.to_thread(model.predict, img, conf=0.25)
        measurements, jpg_bytes = measure_objects(results)

        detections = []

        for m in measurements:
            print(
                f"{m['class']}: {m['length_px']:.1f} px, {m['length_px'] / pixels_per_cm} cm (conf: {m['confidence']:.2f})")
            detections.append(DetectionBox(
                class_name=m['class'],
                length_px=m['length_px'],
                length_cm=m['length_px'] / pixels_per_cm,
                confidence=m['confidence']
            ))

        return PredictionResponse(
            image_width=img.width,
            image_height=img.height,
            image_base64=jpg_bytes,
            detections=detections
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#FIXME
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)