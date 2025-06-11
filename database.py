from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine('postgresql://sayitkamol:0000@localhost:5432/delivery_db',
                       echo=True)

Base = declarative_base()
session = sessionmaker()

