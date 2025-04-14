-- Включение расширения pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Создание таблицы для хранения эмбеддингов пицц
CREATE TABLE IF NOT EXISTS pizza_embeddings (
    id SERIAL PRIMARY KEY,
    class_name TEXT NOT NULL,
    image_name TEXT NOT NULL,
    vector VECTOR(256)
);

-- Уникальный индекс для предотвращения дубликатов по названию пиццы и имени изображения
CREATE UNIQUE INDEX IF NOT EXISTS idx_pizza_embeddings_unique
ON pizza_embeddings (class_name, image_name);
