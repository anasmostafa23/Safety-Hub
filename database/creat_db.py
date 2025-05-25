# create_db.py or in your main file
from sqlalchemy import create_engine
from models import Base , engine # adjust this path

Base.metadata.create_all(engine)
