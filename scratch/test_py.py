from pydantic import BaseModel
from datetime import datetime
class A(BaseModel):
    d: datetime
a = A(d='2030-07-18T17:41:00')
print(repr(a.d))
