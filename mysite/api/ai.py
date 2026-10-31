import asyncio
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from langchain_core.exceptions import OutputParserException
from mysite.database.db import SessionLocal
from mysite.database.models import Course
from mysite.chain.ticket_chain import ticket_chain
from mysite.chain.answer_chain import answer_chain
from mysite.chain.ai_search import search_chain, is_banned
from mysite.schemas.ai_schema import (TicketInputSchema, TicketOutputSchema, AnswerInputSchema, AnswerOutputSchema,
                                      SearchInputSchema, SearchOutputSchema)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ai_router = APIRouter(prefix='/ai', tags=['AI Assistant'])


@ai_router.post(path='/analyze/', response_model=TicketOutputSchema)
async def analyze_ticket(ticket: TicketInputSchema):
    text = ticket.text.strip()

    if not text:
        raise HTTPException(status_code=422, detail='Данные переданы в неверном формате')

    try:
        result = await asyncio.wait_for(
            ticket_chain.ainvoke({"text": text}), timeout=120
        )
    except TimeoutError:
        raise HTTPException(status_code=500, detail='Модель не успела выполнить задачу')


    except OutputParserException as e:

        print(e)

        raise HTTPException(status_code=500, detail='Ответ модели не подходит под схему')

    return result

@ai_router.post(path="/answer/", response_model=AnswerOutputSchema)
async def answer_list(answer: AnswerInputSchema):
    text = answer.text.strip()
    facts = answer.facts.strip()

    if not text:
        raise HTTPException(status_code=422, detail='Данные переданы в неверном формате')

    try:
        result = await asyncio.wait_for(
            answer_chain.ainvoke({"text": text, "facts": facts}), timeout=120
        )
    except TimeoutError:
        raise HTTPException(status_code=500, detail='Модель не успела выполнить задачу')

    except OutputParserException:
        raise HTTPException(status_code=500, detail='Ответ модели не подходит под схему')

    return result
@ai_router.post(path="/search/", response_model=SearchOutputSchema)
async def search_courses(search: SearchInputSchema, db: Session = Depends(get_db)):
    question = search.question.strip()

    if not question:
        raise HTTPException(status_code=422, detail='Данные переданы в неверном формате')

    if is_banned(question):
        raise HTTPException(status_code=400, detail='На такие вопросы не можем ответить')

    try:
        filters = await asyncio.wait_for(
            search_chain.ainvoke({"question": question}), timeout=120
        )
    except TimeoutError:
        raise HTTPException(status_code=500, detail='Модель не успела выполнить задачу')

    except OutputParserException:
        raise HTTPException(status_code=500, detail='Ответ модели не подходит под схему')

    query = db.query(Course).filter(Course.is_active == True)
    if filters.keyword:
        query = query.filter(or_(Course.title.ilike(f'%{filters.keyword}%'),
                                 Course.description.ilike(f'%{filters.keyword}%')))
    if filters.level:
        query = query.filter(Course.level == filters.level)
    if filters.max_duration_weeks is not None:
        query = query.filter(Course.duration_weeks <= filters.max_duration_weeks)
    if filters.min_duration_weeks is not None:
        query = query.filter(Course.duration_weeks >= filters.min_duration_weeks)
    if filters.max_price is not None:
        query = query.filter(Course.price <= filters.max_price)

    return {'filters': filters, 'courses': query.all()}
