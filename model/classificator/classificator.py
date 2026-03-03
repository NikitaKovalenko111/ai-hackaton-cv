import os

from ultralytics import YOLO
import pandas as pd
from pathlib import Path
from utils.model_math import measure_objects
import numpy as np
from sklearn import model_selection, metrics, linear_model

def create_dataset_csv(dataset_dir, output_csv='./dataset_measurements.csv',
                       pixels_per_cm=70, model_path='best.pt'):
    if os.path.exists(output_csv):
        return
    print("=" * 70)
    print("📊 СОЗДАНИЕ CSV С ИЗМЕРЕНИЯМИ ДАТАСЕТА")
    print("=" * 70)

    print(f"\n📥 Загрузка модели: {model_path}")
    model = YOLO(model_path)
    print("✅ Модель загружена")

    dataset_path = Path(dataset_dir)
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    image_paths = []

    for ext in image_extensions:
        image_paths.extend(dataset_path.glob(ext))

    for ext in image_extensions:
        image_paths.extend(dataset_path.rglob(ext))

    image_paths = list(set(image_paths))

    print(f"\n📁 Найдено изображений: {len(image_paths)}")
    print(f"📏 Калибровка: {pixels_per_cm} px/cm")
    print(f"📄 Выходной файл: {output_csv}")
    print("\n" + "=" * 70)

    all_measurements = []

    for i, img_path in enumerate(image_paths, 1):
        print(f"[{i}/{len(image_paths)}] {img_path.name}", end=" ... ")
        results = model.predict(img_path, conf=0.2, imgsz=640)

        measurements = measure_objects(results)
        measurements = measurements[0]

        row = {}

        for m in measurements:
            if 'arugula' in str(img_path):
                row['type'] = 0
            else:
                row['type'] = 1

            if m['class'] == 'root':
                row['root_length'] = m['length_px'] / pixels_per_cm
                row['root_area'] = m['area_px'] / (pixels_per_cm**2)
                if row['root_area'] != 0:
                    row['root_length_area_ratio'] = row['root_length'] / row['root_area']
            if m['class'] == 'stem':
                row['stem_length'] = m['length_px'] / pixels_per_cm
                row['stem_area'] = m['area_px'] / (pixels_per_cm**2)
                if row['stem_area'] != 0:
                    row['stem_length_area_ratio'] = row['stem_length'] / row['stem_area']
            if m['class'] == 'leaf':
                row['leaf_length'] = m['length_px'] / pixels_per_cm
                row['leaf_area'] = m['area_px'] / (pixels_per_cm**2)
                if row['leaf_area'] != 0:
                    row['leaf_length_area_ratio'] = row['leaf_length'] / row['leaf_area']

            if hasattr(row, 'leaf_length') and hasattr(row, 'stem_length'):
                row['leaf_stem_length_ratio'] = row['leaf_length'] / row['stem_length']

        if measurements:
            all_measurements.append(row)
        else:
            print("❌ Ошибка")

    print("\n📊 Создание CSV файла...")
    df = pd.DataFrame(all_measurements)

    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"✅ Сохранено: {output_csv}")

    return df

def prepare_data(data, pixels_per_cm=70):
    row = {'root_length': 0, 'root_area': 0, 'root_length_area_ratio': 0, 'leaf_length': 0, 'leaf_area': 0, 'leaf_length_area_ratio': 0, 'stem_length': 0, 'stem_area': 0, 'stem_length_area_ratio': 0}

    for m in data:
        print(m)
        if m['class'] == 'root':
            row['root_length'] = m['length_px'] / pixels_per_cm
            row['root_area'] = m['area_px'] / (pixels_per_cm**2)
            if row['root_area'] != 0:
                row['root_length_area_ratio'] = row['root_length'] / row['root_area']
        if m['class'] == 'stem':
            row['stem_length'] = m['length_px'] / pixels_per_cm
            row['stem_area'] = m['area_px'] / (pixels_per_cm**2)
            if row['stem_area'] != 0:
                row['stem_length_area_ratio'] = row['stem_length'] / row['stem_area']
        if m['class'] == 'leaf':
            row['leaf_length'] = m['length_px'] / pixels_per_cm
            row['leaf_area'] = m['area_px'] / (pixels_per_cm**2)
            if row['leaf_area'] != 0:
                row['leaf_length_area_ratio'] = row['leaf_length'] / row['leaf_area']

        if hasattr(row, 'leaf_length') and hasattr(row, 'stem_length'):
            row['leaf_stem_length_ratio'] = row['leaf_length'] / row['stem_length']

    X = pd.DataFrame([row])

    return X

def process_dataset(dataset_path):
    df = pd.read_csv(dataset_path)

    df = df.fillna(df.groupby('type').transform('mean'))

    return df

def train_classificator(dataset_path):
    df = pd.read_csv(dataset_path)

    df = process_dataset(dataset_path)

    X = df.drop('type', axis=1)
    y = df['type']

    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.2, random_state=42)

    model = linear_model.LogisticRegression()

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    accuracy = metrics.accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.2f}")

    return model