from ultralytics import YOLO
import numpy as np

class Classifier:
    def __init__(self, model, model_path):
        if model:
            self.classification_model = model
        elif model_path:
            self.classification_model = YOLO(model_path)
        else:
            raise Exception("Unable to load model")

    def get_result(self, image, conf=0.7):
        result = self.classification_model.predict(image, imgsz=320, conf=conf)
        if result:
            _conf = result[0].probs.max()
            _class = result[0].names[result[0].probs.argmax()]
            return _class, _conf
