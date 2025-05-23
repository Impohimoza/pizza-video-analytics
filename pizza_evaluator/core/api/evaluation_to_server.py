import os
import io

import requests
import json
import numpy as np
import threading
import cv2


def send_evaluation_to_server(
    pizza_id: int,
    crust_percentage: float,
    ingredients: list,
    shift: float,
    radius: float,
    photo: np.ndarray
):
    def task():
        # Кодируем в JPEG (или PNG)
        success, encoded_image = cv2.imencode(".jpg", photo)
        if not success:
            raise ValueError("Ошибка кодирования изображения")

        # Оборачиваем как файл
        image_bytes = io.BytesIO(encoded_image.tobytes())
        image_bytes.name = "pizza.jpeg"  # важно, иначе Django может не распознать как файл

        files = {
            'photo': image_bytes
        }

        data = {
            'token': os.getenv("PIZZERIA_TOKEN"),
            'pizza_id': pizza_id,
            'crust_percentage': crust_percentage,
            'radius': radius,
            'shift': shift,
            'ingredients': json.dumps(ingredients)
        }

        try:
            response = requests.post(os.getenv("API_URL"), data=data, files=files)
            print("Ответ:", response.json())
        except Exception:
            print("Ошибка ответа:", response.status_code, response.text)

    # Запускаем отправку в фоне
    threading.Thread(target=task, daemon=True).start()
