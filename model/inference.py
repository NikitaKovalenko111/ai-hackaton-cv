from ultralytics import YOLO
from utils import model_math

print("Введите путь до модели: ")

model_path = input()

print("Введите путь до изображения: ")

img_path = input()

model = YOLO(model_path)

ppc = model_math.calculate_ppc_from_chessboard('model/calib_10.jpg')

results = model.predict(img_path, save=True, conf=0.3)

measures = model_math.measure_objects(results)

for m in measures[0]:
    print(f"Класс: {m['class']}")
    print(f"Длина в пикселях: {m['length_px']}")
    print(f"Длина в сантиметрах: {m['length_px'] / ppc}")
    print(f"Площадь в пикселях: {m['area_px']}")
    print(f"Площадь в сантиметрах: {m['area_px'] / (ppc**2)}")