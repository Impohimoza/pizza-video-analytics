import numpy as np
from ultralytics import YOLO


class IngredientDetector:
    """Класс для детекции ингредиентов по кропу пиццы"""
    def __init__(self,
                 model_path="pizza_evaluator/models/ingredients_detector.pt",
                 conf_thresh=0.3):
        self.model = YOLO(model_path)
        self.conf_thresh = conf_thresh
        self.class_names = self.model.names

    def detect(self, image: np.ndarray) -> list:
        results = self.model.predict(image,
                                     conf=self.conf_thresh,
                                     verbose=False)
        detections = []
        for box in results[0].boxes:
            cls_id = int(box.cls.cpu().numpy()[0])
            name = self.class_names[cls_id]
            detections.append(name)
        return detections
