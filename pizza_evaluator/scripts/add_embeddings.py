import os

import cv2
import numpy as np
from dotenv import load_dotenv
import psycopg2
from tensorflow.keras.models import load_model

# -------------------------
# 1. Конфигурация
# -------------------------

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "pizza_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))

MODEL_PATH = os.getenv("MODEL_PATH", "model/pizza_embedder_tf")
DATASET_DIR = os.getenv("DATASET_DIR", "dataset")
EMBEDDING_DIM = 256

PIZZA_ID = {'0': 1, '1': 2, '2': 3, '3': 4, '4': 5}

# -------------------------
# 2. Функции
# -------------------------


def load_embedding_model(model_path):
    print(f"[MODEL] Загружаем модель: {model_path}")
    return load_model(model_path)


def preprocess_image(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (480, 480))
    img = img.astype("float32") / 255.0
    return np.expand_dims(img, axis=0)


def get_embedding(image_path, model):
    img = cv2.imread(image_path)
    if img is None:
        print(f"[WARNING] Невозможно прочитать изображение: {image_path}")
        return None
    inp = preprocess_image(img)
    vec = model.predict(inp)[0]
    return vec


def insert_embedding(conn, class_name, image_name, vector):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO pizza_embeddings (pizza_id, image_name, vector)
            VALUES (%s, %s, %s)
        """, (PIZZA_ID[class_name], image_name, vector.tolist()))
    conn.commit()
    print(f"[DB] Загружено: {class_name} — {image_name}")


def connect_to_db():
    print("[DB] Подключение к PostgreSQL...")
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# -------------------------
# 3. Основной код
# -------------------------


def main():
    model = load_embedding_model(MODEL_PATH)
    conn = connect_to_db()

    for class_name in os.listdir(DATASET_DIR):
        class_dir = os.path.join(DATASET_DIR, class_name)
        if not os.path.isdir(class_dir):
            continue

        image_paths = [
            f for f in os.listdir(class_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        for image_name in image_paths:
            full_path = os.path.join(class_dir, image_name)
            print(f"[INFO] {class_name}/{image_name}")
            vec = get_embedding(full_path, model)

            if vec is not None and len(vec) == EMBEDDING_DIM:
                insert_embedding(conn, class_name, image_name, vec)

    conn.close()
    print("[DONE] Загрузка завершена.")


if __name__ == "__main__":
    main()
