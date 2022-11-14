import fastapi as _fastapi
import services as _services
import schemas as _schemas
import sqlalchemy.orm as _orm
from typing import List
import auth

auth_handler = auth.AuthHandler()
app = _fastapi.FastAPI()

_services.create_database()

@app.post("/users/", response_model=_schemas.User)
def create_user(user: _schemas.UserCreate, db: _orm.Session=_fastapi.Depends(_services.get_db)):
    db_user = _services.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already in use.")

    return _services.create_user(db=db, user=user)

@app.post("/users/login/")
def login(auth_detail: _schemas.AuthDetail, db: _orm.Session=_fastapi.Depends(_services.get_db)):
    db_user = _services.get_user_by_email(db=db, email=auth_detail.email)

    if db_user is None or not auth_handler.verify_password(auth_detail.password, db_user.hashed_password):
        raise _fastapi.HTTPException(status_code=404, detail="Incorrect credentials.")

    token = auth_handler.encode_token(db_user.email)
    return token 

@app.get("/users/", response_model=List[_schemas.User])
def read_users(skip: int=0, limit: int=10, db: _orm.Session=_fastapi.Depends(_services.get_db)):
    return _services.get_users(db=db, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=_schemas.User)
def read_user(user_id: int, db: _orm.Session=_fastapi.Depends(_services.get_db)):
    db_user = _services.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise _fastapi.HTTPException(status_code=404, detail="User not found.")
    return db_user

# TODO: auth
@app.post("/users/posts", response_model=_schemas.Post)
def create_post(post: _schemas.PostCreate,
    user_id=_fastapi.Depends(auth_handler.auth_wrapper),
    db: _orm.Session=_fastapi.Depends(_services.get_db)):

    db_user = _services.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise _fastapi.HTTPException(status_code=404, detail="User not found.")
    _services.create_post(db=db, post=post, user_id=user_id)

@app.get("/posts/", response_model=List[_schemas.Post])
def read_posts(skip: int=0, limit: int=10, db: _orm.Session=_fastapi.Depends(_services.get_db)):
    return _services.get_posts(db=db, skip=skip, limit=limit)

@app.get("/posts/{post_id}", response_model=_schemas.Post)
def read_post(post_id: int, db: _orm.Session=_fastapi.Depends(_services.get_db)):
    db_post = _services.get_post(db=db, post_id=post_id)
    if db_post is None:
        raise _fastapi.HTTPException(status_code=404, detail="Post not found.")
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int,
    user_id=_fastapi.Depends(auth_handler.auth_wrapper),
    db: _orm.Session=_fastapi.Depends(_services.get_db)):

    db_post = _services.get_post(db=db, post_id=post_id)
    if db_post is None or user_id is None:
        raise _fastapi.HTTPException(status_code=404, detail="Post not found.")
    _services.delete_post(db=db, post_id=post_id)
    return {"message": f"Deleted post {post_id}."}
    
@app.put("/posts/{post_id}")
def update_post(post_id: int,
    post: _schemas.PostCreate,
    user_id=_fastapi.Depends(auth_handler.auth_wrapper),
    db: _orm.Session=_fastapi.Depends(_services.get_db)):

    db_post = _services.get_post(db=db, post_id=post_id)
    if db_post is None:
        raise _fastapi.HTTPException(status_code=404, detail="Post not found.")
    return _services.update_post(db=db, post=post, post_id=post_id)
    
@app.get("/test")
def test(user_id=_fastapi.Depends(auth_handler.auth_wrapper)):
    return {"user_id": user_id}