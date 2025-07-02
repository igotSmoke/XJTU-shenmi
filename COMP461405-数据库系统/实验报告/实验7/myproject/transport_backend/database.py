from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接URL
# 格式：postgresql://user:password@host:port/database
DATABASE_URL = "opengauss://user44:user44_password@localhost:5432/db44?options=-c%20server_version%3D12.0"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 