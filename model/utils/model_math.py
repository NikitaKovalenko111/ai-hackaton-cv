import base64
import numpy as np
import cv2
import glob
from pathlib import Path
from skimage.morphology import skeletonize
from skan import Skeleton, summarize

def get_root_length(mask_param):
    mask = mask_param

    binary = (mask > 0.5).astype(np.uint8)
    
    if np.sum(binary) < 5:
        return 0.0

    skeleton_img = skeletonize(binary > 0)

    if np.sum(skeleton_img) == 0:
        return 0.0

    branch_data = summarize(Skeleton(skeleton_img))
    total_length = branch_data['branch-distance'].sum()

    return total_length

def measure_objects(results, class_names={0: 'leaf', 1: 'root', 2: 'stem'}):
    measurements = []
    res = results[0]
    
    if results[0].masks is not None:
        masks = res.masks.data.cpu().numpy() 
        classes = res.boxes.cls.cpu().numpy()
        confidences = res.boxes.conf.cpu().numpy()
        plotted_image = results[0].plot(
            conf=True,
            line_width=2,
            font_size=13,
            boxes=True,
            labels=True
        )

        orig_h, orig_w = res.orig_shape

        _, buffer = cv2.imencode(".jpg", plotted_image)
        jpg_bytes = buffer.tobytes()
        image_base64 = base64.b64encode(jpg_bytes).decode("utf-8")
        
        for i in range(len(masks)):
            mask = masks[i]
            cls = classes[i]
            conf = confidences[i]

            mask_orig_size = cv2.resize(mask, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
            
            length_px = get_root_length(mask_orig_size)
            
            area_px = np.sum(mask_orig_size > 0.5) 
                
            class_name = class_names.get(int(cls), f'class_{int(cls)}')
            
            measurements.append({
                'class': class_name,
                'class_id': int(cls),
                'length_px': length_px,
                'area_px': area_px,
                'confidence': float(conf),
                'polygon': mask
            })
    return measurements, image_base64

def calculate_ppc_from_chessboard(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    pattern_size = (7, 4) 

    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

    if ret:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        distances = []
        
        for i in range(len(corners2) - 1):
            if (i + 1) % pattern_size[0] != 0:
                d = np.linalg.norm(corners2[i] - corners2[i+1])
                distances.append(d)
                
        ppcm = np.mean(distances)
        
        print(f"Среднее количество пикселей на 1 см (PPCM): {ppcm:.2f}")
        
        return ppcm
    else:
        print("Не удалось найти углы. Попробуйте улучшить освещение или яркость.")
        return None