from ultralytics import YOLO
import numpy as np

class Classifier:
    def __init__(self, model, model_path=None):
        if model:
            self.classification_model = model
        elif model_path:
            self.classification_model = YOLO(model_path)
        else:
            raise Exception("Unable to load model")

    def get_result(self, image, conf=0.8):
        result = self.classification_model.predict(image, imgsz=320, conf=conf)
        if result:
            _conf = float(result[0].probs.max())
            _idx = int(result[0].probs.argmax())
            _class = result[0].names[_idx]
            return _class, _conf
