from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, func

engine = create_engine('postgresql://app:1234@127.0.0.1:5431/app')
Session = sessionmaker(bind=engine)

Base = declarative_base(bind=engine)

class Ad(Base):

    __tablename__ = 'ads'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True, unique=True, index=True)
    description = Column(String, nullable=True)
    creation_time = Column(DateTime, server_default=func.now())
    owner = Column(String, nullable=True)

Base.metadata.create_all()

