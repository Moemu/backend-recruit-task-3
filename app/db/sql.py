import sqlalchemy
from app.core.config import config
from .models import Base

class Database:
    def __init__(self) -> None:
        self.DB_URL = config.db_url
        self._engine = sqlalchemy.create_engine(self.DB_URL, echo = True)

    def __connect(self):
        return self._engine.connect()
    
    def _create_table(self):
        Base.metadata.create_all(self._engine)