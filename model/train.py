from ultralytics import YOLO
import os

def train_model():
    model = YOLO('yolo11n-seg.pt')

    results = model.train(
        data='model/dataset/data.yaml',
        epochs=100,
        imgsz=640,
        batch=8,
        device=0,
        workers=0,
        optimizer='auto',
        patience=50,
        save=True,
        project='model/runs/segment',
        name='plant_seg_v1',
        verbose=True,
        close_mosaic=10,

        mosaic=0.5,
        copy_paste=0.3,
        flipud=0.0,
        fliplr=0.5,
        hsv_h=0.015,
        hsv_s=0.3,
        hsv_v=0.2,
    )

    print("Обучение завершено!")

if __name__ == '__main__':
    train_model()