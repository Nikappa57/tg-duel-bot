from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Bot.database.models import Base


engine = create_engine("sqlite:///database.db?check_same_thread=False")
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

session = Session()