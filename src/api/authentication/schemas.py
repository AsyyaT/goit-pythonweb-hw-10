from pydantic import EmailStr, BaseModel
from pydantic.fields import Field


class SignUpSchema(BaseModel):
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6, max_length=50)


class RequestEmail(BaseModel):
    email: EmailStr


class InfoSchema(BaseModel):
    message: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)


class LoginSuccessSchema(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    access_token: str


class Token(BaseModel):
    access_token: str
    token_type: str

