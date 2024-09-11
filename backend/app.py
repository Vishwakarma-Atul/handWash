from ultralytics import YOLO
import os

from .utils import Classifier

class inferance:
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.classification_model = YOLO(os.path.join(self.path, "models/classifier/best.pt"))
        self.result = { _class:0 for _class in self.classification_model.names.values() }

    def predict(self, image, MAX_COUNT=100):
        classifer = Classifier(model=self.classification_model)
        _class, _conf = classifer.get_result(image)
        if _class:
            self.result[_class] = min(self.result.get(_class, 0)+1, MAX_COUNT)
        return self.result

if __name__ == "__main__":
    infr = inferance()
    result = infr.infer_frames("your/image.jpeg")
    print(result)