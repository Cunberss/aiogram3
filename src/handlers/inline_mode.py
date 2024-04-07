from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from sqlalchemy import select

from src.db.base import get_session
from src.db.models import Question

router = Router(name='callbacks-router')


@router.inline_query()
async def inline_mode_handler(inline_query: InlineQuery):
    tag_search = inline_query.query.split(' ')[-1]
    async with get_session() as session:
        query = select(Question).where(Question.question_text.like(f'%{tag_search}%'))
        result = await session.execute(query)
        answer = result.all()
        if answer:
            faq_list = [[el[0].id, el[0].question_text, el[0].answer] for el in answer]
            list_answer = [InlineQueryResultArticle(
                id=str(el[0]),
                title=el[1],
                description=el[2],
                input_message_content=InputTextMessageContent(
                    message_text='FAQ',
                ),
                parse_mode='HTML'

            ) for el in faq_list]
            print(list_answer)

            await inline_query.answer(list_answer, is_personal=True)
        else:
            print('Ничего нет')

