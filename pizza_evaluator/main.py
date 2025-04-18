import os

from dotenv import load_dotenv

from db.postgres import pg
from streaming.video_stream_processor import VideoStreamProcessor

if __name__ == "__main__":
    try:
        # Загружаем .env
        load_dotenv()

        # Получаем параметры из окружения
        db_config = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", 5432))
        }

        pg.connect(**db_config)

        stream = VideoStreamProcessor(src=0)
        stream.run()

    except KeyboardInterrupt:
        print("[MAIN] Завершение по Ctrl+C")
    finally:
        pg.close()
