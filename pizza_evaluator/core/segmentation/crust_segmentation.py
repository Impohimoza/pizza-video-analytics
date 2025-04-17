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

        masks = []
        if results.masks is None:
            return None
        for mask_tensor, cls in zip(results.masks.data, results.boxes.cls):
            # mask_tensor - это маска в размере input'а модели
            masks.append((mask_tensor.cpu().numpy().astype(np.uint8), cls))
        return masks
