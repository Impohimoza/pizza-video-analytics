import numpy as np
from ultralytics import YOLO


class CrustSegmentation:
    """Класс для сегментации корки пиццы"""
    def __init__(self,
                 model_path="pizza_evaluator/models/crust_segmentation.pt"):
        self.model = YOLO(model_path)

    def detect(self, image: np.ndarray) -> list:
        """Функция для получения сегментированных участков"""
        results = self.model(image, verbose=False)[0]

        return results
