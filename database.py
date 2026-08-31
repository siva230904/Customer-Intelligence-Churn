from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker

from sqlalchemy import URL

driver="mysql+pymysql"
username="root"
password="root"
host="localhost"
port=3306
database="customerchurn"

url=URL.create(
    drivername=driver,
    username=username,
    password=password,
    host=host,
    port=port,
    database=database
)
engine=create_engine(url)

SessionLocal=sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base=declarative_base()


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()