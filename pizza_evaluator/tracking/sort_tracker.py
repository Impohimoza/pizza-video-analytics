import numpy as np

from .sort import Sort


class SortTrackerManager:
    def __init__(self,
                 control_x=400,
                 max_age=10,
                 min_hits=3,
                 iou_threshold=0.5):
        self.sort_tracker = Sort(max_age=max_age,
                                 min_hits=min_hits,
                                 iou_threshold=iou_threshold)
        self.tracked_ids = {}
        self.ready_ids = {}
        self.control_x = control_x  # вертикальная линия контроля

    def update(self, detections: np.ndarray, frame_time: float) -> np.ndarray:
        if len(detections) == 0:
            return np.empty((0, 5))

        tracks = self.sort_tracker.update(np.array(detections))
        ready_to_eval = []

        for tr in tracks:
            x1, y1, x2, y2, track_id = map(int, tr)
            center_x = (x1 + x2) // 2

            # Зарегистрировать появление объекта
            if track_id not in self.ready_ids and center_x <= self.control_x:
                self.ready_ids[track_id] = frame_time

            if track_id not in self.tracked_ids:
                self.tracked_ids[track_id] = None

            if (
                track_id in self.ready_ids
                and (frame_time - self.ready_ids[track_id] > 1.0)
            ):
                ready_to_eval.append([x1, y1, x2, y2, track_id])
        if len(ready_to_eval) == 0:
            return np.empty((0, 5))
        return np.array(ready_to_eval)
