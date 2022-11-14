import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declaritive
import sqlalchemy.orm as _orm

SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = _sql.create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = _declaritive.declarative_base()
