from pydantic import BaseModel, Field
from typing import Optional, List
from mysite.database.models import CourseLevel
from mysite.schemas.course_schema import CourseOutSchema


class TicketInputSchema(BaseModel):
    text: str

class TicketOutputSchema(BaseModel):
    priority: int = Field(description='Приоритет: 1, 2 или 3')
    course_name: Optional[str] = Field(default=None, description='Название курса или null')
    answer: str = Field(description='Вежливый ответ студенту на русском языке в 2-3 предложениях: извинение, возможная причина и что будет сделано дальше')


class AnswerInputSchema(BaseModel):
    text: str
    facts: str

class AnswerOutputSchema(BaseModel):
    text_draft: str = Field(description='Вежливый ответ студенту на русском языке в 2-3 предложениях')
    review: bool = Field(description='true, если менеджеру нужно проверить ответ перед отправкой, иначе false')


class SearchInputSchema(BaseModel):
    question: str

class SearchFilterSchema(BaseModel):
    keyword: Optional[str] = None
    level: Optional[CourseLevel] = None
    max_duration_weeks: Optional[int] = None
    min_duration_weeks: Optional[int] = None
    max_price: Optional[int] = None

class SearchOutputSchema(BaseModel):
    filters: SearchFilterSchema
    courses: List[CourseOutSchema]
