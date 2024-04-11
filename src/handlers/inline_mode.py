from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from src.db.functions import db_get_question

router = Router(name='inline-mode-router')


@router.inline_query()
async def inline_mode_handler(inline_query: InlineQuery):
    tag_search = inline_query.query.split(' ')[-1].lower()
    answer = await db_get_question(tag_search)
    if answer:
        faq_list = [[el[0].id, el[0].question_text, el[0].answer] for el in answer]
        list_answer = [InlineQueryResultArticle(
            id=str(el[0]),
            title=el[1],
            description='Получить ответ',
            input_message_content=InputTextMessageContent(
                message_text=el[2],
            ),
            parse_mode='HTML'

        ) for el in faq_list]
        await inline_query.answer(list_answer, is_personal=True)
    else:
        await inline_query.answer([])

