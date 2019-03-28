from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.interfaces import PoolListener

class ForeignKeyListener(PoolListener):
    def connect(self, dbapi_con, con_record):
        db_cursor = dbapi_con.execute('pragma foreign_keys=ON')

engine = create_engine('sqlite:///database/Security.db', listeners=[ForeignKeyListener()])
metadata = MetaData()
DB_Session = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine)

def init_db():
    metadata.create_all(bind=engine)



