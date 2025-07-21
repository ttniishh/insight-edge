from pydantic import BaseModel
from typing import List

class HeadlineSentiment(BaseModel):
    headline: str
    sentiment: str
    polarity: float

class SentimentalResponse(BaseModel):
    stock: str
    headlines: List[HeadlineSentiment]
    