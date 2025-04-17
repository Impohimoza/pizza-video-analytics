import cv2
from time import time
import numpy as np
import os

from core.detectors.pizza_detector import PizzaDetector
from tracking.sort_tracker import SortTrackerManager
from core.crop_processor import CropProcessor


class VideoStreamProcessor:
    def __init__(self, src=0, control_line_x=400):
        self.cap = cv2.VideoCapture(src)
        self.tracker = SortTrackerManager(control_x=control_line_x)
        self.detector = PizzaDetector(model_path=os.getenv("PIZZA_DETECTOR"))
        self.processor = CropProcessor()
        self.last_eval_time = 0
        self.control_line_x = control_line_x

    def draw_bounding_boxes_with_id(self, img, bboxes, ids, class_names):
        """Функция для отрисовки bounding boxes на видео потоке"""
        for bbox, id_, name in zip(bboxes, ids, class_names):
            cv2.rectangle(img,
                          (int(bbox[0]), int(bbox[1])),
                          (int(bbox[2]), int(bbox[3])),
                          (255, 0, 0),
                          2)
            cv2.putText(img,
                        "ID:" + str(id_) + f": {name}",
                        (int(bbox[0]), int(bbox[1] - 100)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (255, 0, 0),
                        2)
        return img

    def draw_fps_line(self, img, fps):
        """Функция для отрисовки счетчика fps и линии детекции"""
        cv2.putText(
            img,
            f'FPS: {int(fps)}',
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 255, 0),
            2)

        cv2.line(
            img,
            (self.control_line_x, 0),
            (self.control_line_x, img.shape[0]),
            (0, 255, 255),
            1
        )
        return img

    def run(self):
        """Функция для запуска потока и детекции с оценкой """
        print("[INFO] Запуск видеопотока...")
        fps_count = []
        fps = 0
        while True:
            start_time = time()
            ret, frame = self.cap.read()
            if not ret:
                break
            # Детекция пиццы на кадре
            detections_list = self.detector.detect(frame)
            res = self.tracker.update(detections_list, start_time)
            boxes_track = res[:, :-1]
            boxes_ids = res[:, -1].astype(int)

            class_names = []
            # Единоразовая классификация и оценка пиццы
            for box, id_ in zip(boxes_track, boxes_ids):
                if self.tracker.tracked_ids[id_] is None:
                    x1, y1, x2, y2 = box
                    crop = frame[y1:y2, x1:x2]
                    class_name = self.processor.process_crop(crop)
                    self.tracker.tracked_ids[id_] = class_name
                class_names.append(self.tracker.tracked_ids[id_])

            frame = self.draw_bounding_boxes_with_id(frame,
                                                     boxes_track,
                                                     boxes_ids,
                                                     class_names)
            end_time = time()
            fps_now = 1 / np.round(end_time - start_time, 2)
            fps_count.append(fps_now)
            if len(fps_count) == 30:
                fps = np.mean(fps_count)
                fps_count = []
            frame = self.draw_fps_line(frame, fps)

            cv2.imshow("Pizza Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()
