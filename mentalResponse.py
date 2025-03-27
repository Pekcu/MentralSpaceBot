#GigaChat
from langchain.schema import HumanMessage, SystemMessage
from langchain_gigachat.chat_models.gigachat import GigaChat

#other libs
import asyncio

class MentalResponse:
    @staticmethod
    #получает запрос от gigaChat с контекстом пользователя и системы(базовым)
    async def gigachat_response(user_input: str, giga: GigaChat) -> str:
        bot_messages = [
            SystemMessage(
                content="Ты эмпатичный бот-психолог, который помогает пользователю решить его проблемы. Пользователь - студент, который хочет получить поддержку. Если пользователь набрал бессмесленный текст, ответ должен быть просьбой ввести нормальный запрос, чтобы ты мог ему помочь."
            ),
            HumanMessage(content=user_input)
        ]
        try:
            bot_res: AIMessage  = await asyncio.wait_for(giga.ainvoke(bot_messages), timeout=5.0)
        except asyncio.TimeoutError:
            bot_res = "Помощник временно не доступен😴💤💤"

        return bot_res.content