from ultralytics import YOLO

def train_model():
    model = YOLO('yolo11n-seg.pt')

    results = model.train(
        data='model/dataset/data.yaml',
        epochs=50,
        imgsz=640,
        batch=4,
        device=0,
        workers=8,
        optimizer='Adam',
        patience=50,
        save=True,
        project='model/runs/segment',
        name='plant_seg_v1',
        verbose=True
    )

    print("✅ Обучение завершено!")
    print(f"Лучшая модель сохранена в: runs/segment/plant_seg_v1/weights/best.pt")

if __name__ == '__main__':
    train_model()