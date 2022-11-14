import database as _database
import sqlalchemy.orm as _orm
import models as _models
import schemas as _schemas
from auth import AuthHandler as _auth_handler
import datetime as _dt

auth_handler = _auth_handler()

def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_email(db: _orm.Session, email: str):
    return db.query(_models.User).filter(_models.User.email == email).first()

def create_user(db: _orm.Session, user: _schemas.UserCreate):
    hashed_password = auth_handler.get_password_hash(user.password)
    db_user = _models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: _orm.Session, skip: int, limit: int):
    return db.query(_models.User).offset(skip).limit(limit).all()

def get_user(db: _orm.Session, user_id: int):
    return db.query(_models.User).filter(_models.User.id == user_id).first()

def create_post(db: _orm.Session, post: _schemas.PostCreate, user_id: int):
    post = _models.Post(**post.dict(), owner_id=user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def get_posts(db: _orm.Session, skip: int, limit: int):
    return db.query(_models.Post).offset(skip).limit(limit).all()

def get_post(db: _orm.Session, post_id: int):
    return db.query(_models.Post).filter(_models.Post.id == post_id).first()

def delete_post(db: _orm.Session, post_id: int):
    db.query(_models.Post).filter(_models.Post.id == post_id).delete()
    db.commit()
    
def update_post(db: _orm.Session, post: _schemas.PostCreate, post_id: int):
    db_post = get_post(db=db, post_id=post_id)
    db_post.title = post.title
    db_post.content = post.content
    db_post.date_last_updated = _dt.datetime.utcnow()
    db.commit()
    db.refresh(db_post)
    return db_post
    