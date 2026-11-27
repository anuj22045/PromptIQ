
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()


def get_database_engine():

    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME")
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True
    )

    return engine


def test_database_connection():

    engine = None

    try:
        engine = get_database_engine()

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT current_database()")
            )

            database_name = result.scalar()

        return {
            "connected": True,
            "database": database_name,
            "error": None
        }

    except Exception as e:

        return {
            "connected": False,
            "database": None,
            "error": str(e)
        }

    finally:
        if engine is not None:
            engine.dispose()
