from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/custchurn"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()