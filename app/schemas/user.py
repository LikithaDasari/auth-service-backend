from pydantic import constr, BaseModel

class CreateUser(BaseModel):
    username: constr(min_length=4, strip_whitespace=True) # type: ignore
    password: constr(min_length=8, strip_whitespace=True) # type: ignore
