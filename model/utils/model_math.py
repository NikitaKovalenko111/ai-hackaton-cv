import base64
import numpy as np
import cv2
import glob
from pathlib import Path
from skimage.morphology import medial_axis
from scipy.spatial import cKDTree

def create_binary_mask(polygon, img_shape):
    h, w = img_shape
    binary = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(binary, [polygon.astype(np.int32)], 255)
    return binary

def skeletonize_mask(binary_mask):
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    skeleton = cv2.ximgproc.thinning(
        cleaned, 
        thinningType=cv2.ximgproc.THINNING_ZHANGSUEN
    )
    
    return skeleton

def calculate_skeleton_length(skeleton):
    return cv2.countNonZero(skeleton)

def calculate_polygon_area(polygon: np.ndarray) -> float:
    if len(polygon) < 3:
        return 0.0
    
    x = polygon[:, 0]
    y = polygon[:, 1]

    area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    return float(area)

def measure_objects(results, class_names={0: 'leaf', 1: 'root', 2: 'stem'}):
    measurements = []
    
    if results[0].masks is not None:
        masks = results[0].masks.xy
        classes = results[0].boxes.cls.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()
        plotted_image = results[0].plot(
            conf=True,
            line_width=2,
            font_size=13,
            boxes=True,
            labels=True
        )

        _, buffer = cv2.imencode(".jpg", plotted_image)
        jpg_bytes = buffer.tobytes()
        image_base64 = base64.b64encode(jpg_bytes).decode("utf-8")
        
        for mask, cls, conf in zip(masks, classes, confidences):
            length = 0
            if cls == 'root':
                length = calculate_skeleton_length(mask, plotted_image.shape[:2])
            else:
                length = 0
                for i in range(len(mask)):
                    for j in range(i + 1, len(mask)):
                        dist = np.sqrt(np.sum((mask[i] - mask[j])**2))
                        length = max(length, dist)
                
            class_name = class_names.get(int(cls), f'class_{int(cls)}')

            area = calculate_polygon_area(mask)
            
            measurements.append({
                'class': class_name,
                'class_id': int(cls),
                'length_px': length,
                'area_px': area,
                'confidence': float(conf),
                'polygon': mask
            })
    return measurements, image_base64

def getPpc():
    return 85

def calibrate_camera(calibration_images_folder, chessboard_size=(4, 7)):   
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 
                30, 0.001)
    
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
    
    objp *= 1.0
    
    objpoints = []
    imgpoints = []
    
    images = list(Path(calibration_images_folder).glob('*.jpg')) + \
             list(Path(calibration_images_folder).glob('*.png'))
    
    print(f"Найдено {len(images)} калибровочных изображений")
    
    for fname in images:
        img = cv2.imread(str(fname))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
        
        if ret:
            objpoints.append(objp)
            
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)
            
            cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)
            print(f"{fname.name}: найдены углы")
    
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )
    
    print(f"\nРезультаты калибровки:")
    print(f"  RMS ошибка: {ret:.4f} пикселей")
    print(f"  Camera matrix:\n{camera_matrix}")
    print(f"  Distortion coefficients: {dist_coeffs.ravel()}")
    
    fx = camera_matrix[0, 0]
    fy = camera_matrix[1, 1]
    pixels_per_cm = (fx + fy) / 2
    
    print(f"\nPixels per cm: {pixels_per_cm:.2f}")
    
    return camera_matrix, dist_coeffs, pixels_per_cm

def calculate_ppc_from_chessboard(image_path, chessboard_size=(4, 7), square_size_cm=1.0):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size)
    
    if ret:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        
        width_px = corners[-1][0][0] - corners[0][0][0]
        height_px = corners[-chessboard_size[0]][0][1] - corners[0][0][1]
        
        width_cm = chessboard_size[0] * square_size_cm
        height_cm = chessboard_size[1] * square_size_cm
        
        ppc_width = width_px / width_cm
        ppc_height = height_px / height_cm
        pixels_per_cm = (ppc_width + ppc_height) / 2
        
        print(f"Ширина: {width_px:.0f} px = {width_cm:.1f} см → {ppc_width:.2f} px/cm")
        print(f"Высота: {height_px:.0f} px = {height_cm:.1f} см → {ppc_height:.2f} px/cm")
        print(f"pixels_per_cm = {pixels_per_cm:.2f}")
        
        return pixels_per_cm
    else:
        print("Углы не найдены")
        return None