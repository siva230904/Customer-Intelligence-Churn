from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="root",
    host="localhost",
    port=3306,
    database="custchurn"
)

engine = create_engine(connection_url)
Base = declarative_base()

Sessionlocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

def get_db():
    db = Sessionlocal()
    return db