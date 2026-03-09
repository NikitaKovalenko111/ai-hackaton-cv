import cv2
import numpy as np
import shutil
from pathlib import Path
import random

class ArugulaAugmenter:
    def __init__(self, dataset_path, multiplier=5):
        """
        dataset_path: путь к датасету
        multiplier: во сколько раз умножить рукколу
        """
        self.dataset_path = Path(dataset_path)
        self.multiplier = multiplier
        self.train_images = self.dataset_path / 'train' / 'images'
        self.train_labels = self.dataset_path / 'train' / 'labels'
        
    def find_arugula_images(self):
        arugula_files = []
        
        for img_path in self.train_images.glob('*.jpg'):
            if img_path.stem.lower().startswith('arugula'):
                arugula_files.append(img_path.stem)
        
        for img_path in self.train_images.glob('*.jpeg'):
            if img_path.stem.lower().startswith('arugula'):
                arugula_files.append(img_path.stem)
        
        for img_path in self.train_images.glob('*.png'):
            if img_path.stem.lower().startswith('arugula'):
                arugula_files.append(img_path.stem)
        
        print(f"📊 Найдено {len(arugula_files)} изображений с рукколой (по имени файла)")
        
        if arugula_files:
            print(f"   Примеры: {arugula_files[:5]}")
        
        return arugula_files
    
    def augment_image(self, img, aug_type):
        
        if aug_type == 'flip':
            return cv2.flip(img, 1)
        
        elif aug_type == 'bright_up':
            return cv2.convertScaleAbs(img, alpha=1.15, beta=20)
        
        elif aug_type == 'bright_down':
            return cv2.convertScaleAbs(img, alpha=0.85, beta=-20)
        
        elif aug_type == 'contrast_up':
            return cv2.convertScaleAbs(img, alpha=1.2, beta=0)
        
        elif aug_type == 'contrast_down':
            return cv2.convertScaleAbs(img, alpha=0.8, beta=0)
        
        return img
    
    def transform_coordinates(self, coords, aug_type):
        
        new_coords = coords.copy()
        
        if aug_type == 'flip':
            for i in range(0, len(new_coords), 2):
                new_coords[i] = 1.0 - new_coords[i]
        
        
        return new_coords
    
    def augment(self):
        """Запустить аугментацию только для рукколы"""
        
        arugula_files = self.find_arugula_images()
        
        if not arugula_files:
            print("❌ Изображения с рукколой не найдены!")
            print("   Проверьте, что файлы начинаются с 'arugula' (например, arugula_001.jpg)")
            return
        
        # Аугментации
        augmentations = [
            'flip',
            'bright_up',
            'bright_down',
            'contrast_up',
            'contrast_down',
        ]
        
        total_created = 0
        
        for i in range(1, self.multiplier):
            aug_type = augmentations[(i - 1) % len(augmentations)]
            created_count = 0
            
            for img_name in arugula_files:
                img_path = None
                for ext in ['.jpg', '.jpeg', '.png']:
                    path = self.train_images / f"{img_name}{ext}"
                    if path.exists():
                        img_path = path
                        break
                
                if img_path is None:
                    continue
                
                img = cv2.imread(str(img_path))
                
                if img is None:
                    print(f"   ⚠️  Не удалось загрузить {img_path}")
                    continue
                
                img_aug = self.augment_image(img, aug_type)
                
                new_name = f"{img_name}_aug{i}_{aug_type}"
                dst_img_path = self.train_images / f"{new_name}.jpg"
                dst_lbl_path = self.train_labels / f"{new_name}.txt"
                
                cv2.imwrite(str(dst_img_path), img_aug)
                
                src_lbl_path = None
                for ext in ['.txt']:
                    path = self.train_labels / f"{img_name}{ext}"
                    if path.exists():
                        src_lbl_path = path
                        break
                
                if src_lbl_path and src_lbl_path.exists():
                    with open(src_lbl_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    new_lines = []
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            cls = parts[0]
                            coords = list(map(float, parts[1:]))
                            
                            if aug_type == 'flip':
                                new_coords = self.transform_coordinates(
                                    np.array(coords), aug_type
                                )
                                new_line = f"{cls} " + " ".join([f"{c:.6f}" for c in new_coords]) + "\n"
                            else:
                                new_line = line
                            
                            new_lines.append(new_line)
                    
                    with open(dst_lbl_path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                else:
                    print(f"   ⚠️  Label файл не найден для {img_name}")
                
                created_count += 1
            
            total_created += created_count
            print(f"  ✅ Аугментация {i} ({aug_type}): {created_count} файлов")
        
        print(f"\n🎉 Готово! Создано {total_created} новых изображений с рукколой")
        print(f"   Было: {len(arugula_files)} → Стало: {len(arugula_files) * self.multiplier}")

if __name__ == '__main__':
    augmenter = ArugulaAugmenter(
        dataset_path='model/dataset',
        multiplier=7 
    )
    augmenter.augment()