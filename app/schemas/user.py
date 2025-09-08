from pydantic import constr, BaseModel
from typing import Annotated

class CreateUser(BaseModel):
    username: Annotated[str, constr(min_length=4)]
    password: Annotated[str, constr(min_length=8)]