from ultralytics import YOLO
import os

from .utils import Classifier


class inferance:
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.classification_model = YOLO(os.path.join(self.path, "models/classifier/best.pt"))
        self._result = { _class:0 for _class in self.classification_model.names.values() }
        self.classifier = Classifier(model=self.classification_model)

    def predict(self, image, MAX_COUNT=100):
        conf = 0.75
        result = self.classifier.get_result(image, conf=conf)
        if result:
            _class, _conf = result
            if _class and _conf >= conf:
                self._result[_class] = min(self._result.get(_class, 0)+1, MAX_COUNT)
                return self._result

if __name__ == "__main__":
    infr = inferance()
    result = infr.predict("your/image.jpeg")
    print(result)