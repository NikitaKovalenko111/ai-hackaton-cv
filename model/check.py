from ultralytics import YOLO
from classificator import classificator
from utils import model_math

#model = YOLO('model/runs/segment/plant_seg_v12/weights/best.pt')

classificatorModel = classificator.train_classificator('model/classificator/dataset_measurements.csv')