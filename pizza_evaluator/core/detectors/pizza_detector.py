import numpy as np
from ultralytics import YOLO


class PizzaDetector:
    """Класс для детектирования пиццы"""
    def __init__(self,
                 model_path='pizza_evaluator/models/yolov8m.pt',
                 conf_thresh=0.5):
        self.model = YOLO(model_path)
        self.conf_thresh = conf_thresh

    def get_results(self, results: list) -> np.ndarray:
        """Функция для обработки результата модели детекции"""
        detection_list = []
        for result in results[0]:
            confidence = result.boxes.conf.cpu().numpy()
            class_id = result.boxes.cls.cpu().numpy().astype(int)
            if confidence[0] > 0.75 and class_id == 53:
                bbox = result.boxes.xyxy.cpu().numpy()
                merged_detection = [bbox[0][0],
                                    bbox[0][1],
                                    bbox[0][2],
                                    bbox[0][3],
                                    confidence[0]]
                detection_list.append(merged_detection)
        return np.array(detection_list)

    def detect(self, frame: np.ndarray) -> np.ndarray:
        """
        Детектирует пиццу на кадре
        """
        results = self.model.predict(frame,
                                     conf=self.conf_thresh,
                                     verbose=False)

        detections_list = self.get_results(results)
        return detections_list
