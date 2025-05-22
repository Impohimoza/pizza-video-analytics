import cv2
import numpy as np


class FillingCenterChecker:
    def preprocessing_segmentation(self,
                                   segmentation_result,
                                   image: np.ndarray
                                   ) -> tuple[np.ndarray, np.ndarray]:
        """Метод для получения масок корки и начинки"""
        masks = segmentation_result.masks.data.cpu().numpy()  # (N, H, W)
        classes = segmentation_result.boxes.cls.cpu().numpy()  # классы масок

        # поиск маски начинки (например, class_id == 1)
        filling_mask = None
        for i, cls_id in enumerate(classes):
            if int(cls_id) == 1:  # ID начинки
                filling_mask = masks[i]
                break

        if filling_mask is None:
            raise ValueError("Маска начинки не найдена")

        # Переводим маску в бинарную (0 и 1)
        filling_mask_bin = (filling_mask > 0.5).astype(np.uint8)

        # Resize до исходного размера изображения
        filling_mask_bin = cv2.resize(filling_mask_bin,
                                      (image.shape[1], image.shape[0]),
                                      interpolation=cv2.INTER_NEAREST)

        crust_mask = None
        for i, cls_id in enumerate(classes):
            if int(cls_id) == 0:
                crust_mask = masks[i]
                break

        if crust_mask is None:
            raise ValueError("Маска начинки не найдена")

        # Переводим маску в бинарную (0 и 1)
        crust_mask_bin = (crust_mask > 0.5).astype(np.uint8)

        # Resize до исходного размера изображения
        crust_mask_bin = cv2.resize(crust_mask_bin,
                                    (image.shape[1], image.shape[0]),
                                    interpolation=cv2.INTER_NEAREST)
        return filling_mask_bin, crust_mask_bin

    def compute_center_shift(self, image: np.ndarray, segmentation_result):
        """
        Оценка смещения начинки относительно центра пиццы.

        :param filling_mask: бинарная маска начинки
        :param crust_mask: бинарная маска корки
        :return: смещение и радиус пиццы
        """
        filling_mask, crust_mask = self.preprocessing_segmentation(
            segmentation_result,
            image
        )
        # Центр пиццы = центр ограничивающего прямоугольника по маске
        pizza_mask = np.clip(filling_mask + crust_mask, 0, 1).astype(np.uint8)
        ys, xs = np.where(pizza_mask > 0)
        if len(xs) == 0 or len(ys) == 0:
            return 0.0  # нет маски пиццы

        pizza_center = np.array([np.mean(xs), np.mean(ys)])

        # Центр тяжести начинки
        fy, fx = np.where(filling_mask > 0)
        if len(fx) == 0 or len(fy) == 0:
            return 0.0  # нет начинки

        filling_center = np.array([np.mean(fx), np.mean(fy)])
        print

        # Радиус пиццы = половина диагонали ограничивающего прямоугольника
        x_min, x_max = xs.min(), xs.max()
        y_min, y_max = ys.min(), ys.max()
        radius = 0.5 * np.sqrt((x_max - x_min)**2 + (y_max - y_min)**2)

        # Смещение
        shift = np.linalg.norm(pizza_center - filling_center)
        return shift, radius
