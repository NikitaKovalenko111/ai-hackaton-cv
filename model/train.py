from ultralytics import YOLO
import os

def train_model():
    model = YOLO('yolo11s-seg.pt')

    results = model.train(
        data='./dataset/data.yaml',
        epochs=150,
        imgsz=640,
        batch=4,
        device=0,
        workers=8,
        optimizer='Adam',
        patience=50,
        save=True,
        project='./runs/segment',
        name='plant_seg_v2',
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