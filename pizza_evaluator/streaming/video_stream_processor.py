import cv2
from time import time
import numpy as np

from detectors.pizza_detector import PizzaDetector
from tracking.sort_tracker import SortTrackerManager


class VideoStreamProcessor:
    def __init__(self, src=0, control_line_x=400):
        self.cap = cv2.VideoCapture(src)
        self.tracker = SortTrackerManager(control_x=control_line_x)
        self.detector = PizzaDetector()
        self.last_eval_time = 0
        self.control_line_x = control_line_x

    def draw_bounding_boxes_with_id(self, img, bboxes, ids):
        for bbox, id_ in zip(bboxes, ids):
            cv2.rectangle(img,
                          (int(bbox[0]), int(bbox[1])),
                          (int(bbox[2]), int(bbox[3])),
                          (255, 0, 0),
                          2)
            cv2.putText(img,
                        "ID:" + str(id_),
                        (int(bbox[0]), int(bbox[1] - 100)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (255, 0, 0),
                        2)
        return img

    def run(self):
        print("[INFO] Запуск видеопотока...")
        fps_count = []
        fps = 0
        while True:
            start_time = time()
            ret, frame = self.cap.read()
            if not ret:
                break
            detections_list = self.detector.detect(frame)
            res = self.tracker.update(detections_list, start_time)
            boxes_track = res[:, :-1]
            boxes_ids = res[:, -1].astype(int)

            frame = self.draw_bounding_boxes_with_id(frame,
                                                     boxes_track,
                                                     boxes_ids)
            end_time = time()
            fps_now = 1 / np.round(end_time - start_time, 2)
            fps_count.append(fps_now)
            if len(fps_count) == 30:
                fps = np.mean(fps_count)
                fps_count = []
            cv2.putText(frame,
                        f'FPS: {int(fps)}',
                        (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        (0, 255, 0),
                        2)

            cv2.line(
                frame,
                (self.control_line_x, 0),
                (self.control_line_x, frame.shape[0]),
                (0, 255, 255),
                1
            )

            cv2.imshow("Pizza Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()
