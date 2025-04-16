-- Расширение для работы с векторами
CREATE EXTENSION IF NOT EXISTS vector;

-- Таблица с видами пицц
CREATE TABLE IF NOT EXISTS pizzas (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Таблица с ингредиентами
CREATE TABLE IF NOT EXISTS ingredients (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Таблица, описывающая состав каждой пиццы
CREATE TABLE IF NOT EXISTS pizza_composition (
    pizza_id INTEGER REFERENCES pizzas(id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (pizza_id, ingredient_id)
);

-- Таблица с эмбеддингами изображений пицц
CREATE TABLE IF NOT EXISTS pizza_embeddings (
    id SERIAL PRIMARY KEY,
    pizza_id INTEGER REFERENCES pizzas(id) ON DELETE CASCADE,
    image_name TEXT NOT NULL,
    vector VECTOR(256),
    UNIQUE (pizza_id, image_name)
);

