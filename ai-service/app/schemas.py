from pydantic import BaseModel
from typing import Optional, List

class Product(BaseModel):
    row_index: int
    name: str
    image_url: Optional[str] = None

class Source(BaseModel):
    shop: str
    url: str

class MatchResult(BaseModel):
    name: str
    found: bool
    sources: List[Source]



from pydantic import BaseModel
from typing import Optional, List

class Product(BaseModel):
    row_index: int
    name: str
    image_url: Optional[str] = None

class Source(BaseModel):
    shop: str
    url: str
    score: Optional[float] = None

class MatchResult(BaseModel):
    name: str
    found: bool
    sources: List[Source]
