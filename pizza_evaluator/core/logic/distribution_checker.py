import numpy as np
import cv2


class DistributionChecker:
    """Класс для подсчета распределение ингредиентов по начинке"""
    def __init__(self, min_overlap_ratio=0.3):
        self.min_overlap_ratio = min_overlap_ratio

    def preprocessing_segmentation(self,
                                   segmentation_result,
                                   image: np.ndarray) -> np.ndarray:
        """Метод для получения маски начинки"""
        masks = segmentation_result.masks.data.cpu().numpy()  # (N, H, W)
        classes = segmentation_result.boxes.cls.cpu().numpy()  # классы масок

        # Найдём маску начинки (например, class_id == 1)
        filling_mask = None
        for i, cls_id in enumerate(classes):
            if int(cls_id) == 1:  # замените на ID начинки
                filling_mask = masks[i]
                break

        if filling_mask is None:
            raise ValueError("Маска начинки не найдена")

        # Переводим маску в бинарную (0 и 1)
        filling_mask_bin = (filling_mask > 0.5).astype(np.uint8)

        # Resize до исходного размера изображения (если нужно)
        filling_mask_bin = cv2.resize(filling_mask_bin,
                                      (image.shape[1], image.shape[0]),
                                      interpolation=cv2.INTER_NEAREST)
        return filling_mask_bin

    def preprocessing_detection(self, detection_result):
        """Метод для получения обнаруженных ингредиентов"""
        boxes = []
        for box, cls in zip(detection_result.boxes.xyxy.cpu().numpy(),
                            detection_result.boxes.cls.cpu().numpy()):
            x1, y1, x2, y2 = box
            class_id = int(cls)
            boxes.append((x1, y1, x2, y2, class_id))
        return boxes

    def ingredient_distribution_score(self,
                                      image: np.ndarray,
                                      detection_result,
                                      segmentation_result) -> dict:
        """
        Оценка равномерности распределения ингредиента:
        Ячейка считается заполненной, если один из объектов ингредиента
        покрывает в ней >= min_overlap_ratio от площади ячейки.

        :param mask: бинарная маска начинки (2D NumPy)
        :param boxes: список (x1, y1, x2, y2, class_id)
        :param min_overlap_ratio: минимальная доля площади ячейки
        :return: словарь {class_id: score}, где score в [0, 1]
        """
        mask = self.preprocessing_segmentation(segmentation_result, image)
        boxes = self.preprocessing_detection(detection_result[0])
        h, w = mask.shape
        scores = {}
        ingredient_classes = sorted(set(cls for *_, cls in boxes))

        ys, xs = np.where(mask > 0)
        if len(xs) == 0 or len(ys) == 0:
            return {cls: 0.0 for cls in ingredient_classes}

        x_min, x_max = xs.min(), xs.max()
        y_min, y_max = ys.min(), ys.max()

        filling_h = y_max - y_min + 1
        filling_w = x_max - x_min + 1

        for cls_id in ingredient_classes:
            ing_boxes = [(x1, y1, x2, y2) for (x1, y1, x2, y2, c) in boxes if c == cls_id]
            num_boxes = len(ing_boxes)
            if num_boxes == 0:
                scores[cls_id] = 0.0
                continue

            # Сетка по количеству объектов
            grid_rows = int(np.floor(np.sqrt(num_boxes)))
            grid_cols = int(np.floor(num_boxes / grid_rows))
            cell_h = filling_h // grid_rows
            cell_w = filling_w // grid_cols

            filled_cells = 0
            total_cells = 0

            for i in range(grid_rows):
                for j in range(grid_cols):
                    # Границы ячейки в координатах оригинального изображения
                    y1 = y_min + i * cell_h
                    y2 = min(y_min + (i + 1) * cell_h, h)
                    x1 = x_min + j * cell_w
                    x2 = min(x_min + (j + 1) * cell_w, w)

                    filling_cell = mask[y1:y2, x1:x2]
                    if np.sum(filling_cell) == 0:
                        continue  # вне пиццы

                    max_overlap = 0

                    for (bx1, by1, bx2, by2) in ing_boxes:
                        # Пересечение текущего бокса с ячейкой
                        ix1 = max(x1, int(bx1))
                        iy1 = max(y1, int(by1))
                        ix2 = min(x2, int(bx2))
                        iy2 = min(y2, int(by2))
                        if ix1 >= ix2 or iy1 >= iy2:
                            continue
                        intersection_area = (ix2 - ix1) * (iy2 - iy1)
                        overlap_ratio = intersection_area / ((bx2 - bx1) * (by2 - by1))
                        max_overlap = max(max_overlap, overlap_ratio)

                    if max_overlap >= self.min_overlap_ratio:
                        filled_cells += 1
                    total_cells += 1

            scores[cls_id] = filled_cells / total_cells if total_cells > 0 else 0.0

        return scores
