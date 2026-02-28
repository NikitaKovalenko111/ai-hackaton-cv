from ultralytics import YOLO
import os

def train_model():
    model = YOLO('yolo11n-seg.pt')

    results = model.train(
        data='model/dataset/data.yaml',
        epochs=os.environ.get('TRAIN_EPOCHS'),
        imgsz=os.environ.get('TRAIN_IMGSZ'),
        batch=os.environ.get('TRAIN_BATCH'),
        device=os.environ.get('TRAIN_DEVICE'),
        workers=os.environ.get('TRAIN_WORKERS'),
        optimizer='Adam',
        patience=os.environ.get('TRAIN_PATIENCE'),
        save=True,
        project='model/runs/segment',
        name='plant_seg_v1',
        verbose=True,
        close_mosaic=10
    )

    print("Обучение завершено!")

if __name__ == '__main__':
    train_model()