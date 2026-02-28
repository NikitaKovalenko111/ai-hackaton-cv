from ultralytics import YOLO
import cv2
import numpy as np
from utils.model_math import measure_objects, calculate_ppc_from_chessboard
from utils.preprocessing import auto_orient
from dotenv import load_dotenv

load_dotenv('.env')

model = YOLO('./runs/segment/plant_seg_v14/weights/best.pt')

print("Модель загружена!")

pixels_per_cm = calculate_ppc_from_chessboard(
    './dataset/calibrate/calib_10.jpg',
    chessboard_size=(4, 7),
    square_size_cm=1.0
)

img = auto_orient('arugula_20260219162931907.jpg')
results = model.predict(img, conf=0.25, save=True)

measurements = measure_objects(results)

for m in measurements:
    print(f"{m['class']}: {m['length_px']:.1f} px, {m['length_px'] / pixels_per_cm} cm (conf: {m['confidence']:.2f})")