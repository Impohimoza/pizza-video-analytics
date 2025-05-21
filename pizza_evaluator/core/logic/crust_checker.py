import cv2
import numpy as np

from ..segmentation.crust_segmentation import CrustSegmentation


class CrustChecker:
    """Класс для получения процента корки на пицце"""

    def get_percentage_crust(self, image: np.ndarray, segmentation_result) -> float:
        """Функция для расчета процента корки
        на пицце по маскам корки и начинки"""
        masks = []
        if segmentation_result.masks is None:
            return None
        for mask_tensor, cls in zip(segmentation_result.masks.data, segmentation_result.boxes.cls):
            # mask_tensor - это маска в размере input'а модели
            masks.append((mask_tensor.cpu().numpy().astype(np.uint8), cls))

        if masks is None:
            return 0.0

        original_h, original_w = image.shape[:2]

        # Подготовка пустых масок
        mask_crust = np.zeros((original_h, original_w), dtype=np.uint8)
        mask_topping = np.zeros((original_h, original_w), dtype=np.uint8)

        # Проход по всем маскам
        for mask_tensor, cls in masks:
            mask_resized = cv2.resize(
                mask_tensor,
                (original_w, original_h),
                interpolation=cv2.INTER_NEAREST
            )

            # Объединять маски нескольких объектов, если модель нашла несколько фрагментов корки
            if int(cls) == 0:   # crust
                mask_crust = np.maximum(mask_crust, mask_resized)
            elif int(cls) == 1:     # topping
                mask_topping = np.maximum(mask_topping, mask_resized)

        # Вычисление площадей
        area_crust = np.sum(mask_crust)
        area_topping = np.sum(mask_topping)

        # Проверка на деление на 0
        total_area = area_crust + area_topping
        percent_crus = (area_crust / total_area * 100) if total_area > 0 else 0
        return percent_crus