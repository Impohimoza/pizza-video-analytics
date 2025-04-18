from collections import Counter

from db.postgres import pg


def find_closest_class(vector, top_k=3) -> str:
    """Функция для получения класса пиццы путем knn"""
    cursor = pg.get_cursor()
    if cursor is None:
        raise ValueError("Не передан psycopg2 cursor")

    query = """
        SELECT pizza_id, vector <#> %s::vector AS similarity
        FROM pizza_embeddings
        ORDER BY similarity ASC
        LIMIT %s
    """
    cursor.execute(query, (vector.tolist(), top_k))
    results = cursor.fetchall()
    if not results:
        return "Unknown"

    # Реализация knn
    top_classes = [row[0] for row in results]  # row[0] = class_name
    majority_class = Counter(top_classes).most_common(1)[0][0]
    return majority_class
