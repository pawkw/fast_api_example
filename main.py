from fastapi import FastAPI, HTTPException, Depends
from auth import AuthHandler
from schemas import AuthDetail

app = FastAPI()
auth_handler = AuthHandler()

users = []

@app.post("/register", status_code=201)
def register(auth_detail: AuthDetail):
    if any(x['username'] == auth_detail.username for x in users):
        raise HTTPException(status_code=400, detail="Username is taken.")
    
    hashed_password = auth_handler.get_password_hash(auth_detail.password)
    users.append({
        'username': auth_detail.username,
        'password': hashed_password
    })
    return

@app.post("/login")
def login(auth_detail: AuthDetail):
    user = None
    for x in users:
        if x['username'] == auth_detail.username:
            user = x
            break
    
    if user is None or not auth_handler.verify_password(auth_detail.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = auth_handler.encode_token(user['username'])
    return {'token': token}

@app.get('/public')
def public():
    return {"data": "public data"}

@app.get('/privileged')
def privileged(username=Depends(auth_handler.auth_wrapper)):
    return {"username": username}