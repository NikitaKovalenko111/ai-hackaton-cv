import cv2
from PIL import Image, ImageOps
import numpy as np

def auto_orient(img):
    img = ImageOps.exif_transpose(img)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)