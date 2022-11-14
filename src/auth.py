import jwt
import fastapi as _fastapi
import fastapi.security as _security
import passlib.context as _context
import datetime as _dt

class AuthHandler:
    security = _security.HTTPBearer()
    password_context = _context.CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = "b20e93cb55ee2637eca6298d1ba07eb5"

    def get_password_hash(self, password):
        return self.password_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.password_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id):
        payload = {
            'exp': _dt.datetime.utcnow() + _dt.timedelta(days=0, minutes=30),
            'iat': _dt.datetime.utcnow(),
            'sub': user_id
        }
        
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise _fastapi.HTTPException(status_code=401, detail='Signature has expired.')
        except jwt.InvalidTokenError as e:
            raise _fastapi.HTTPException(status_code=401, detail='Invalid token.')

    def auth_wrapper(self, auth: _security.HTTPAuthorizationCredentials = _fastapi.Security(security)):
        return self.decode_token(auth.credentials)