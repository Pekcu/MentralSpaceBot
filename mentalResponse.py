#GigaChat
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.messages import AIMessage
from langchain_gigachat.chat_models.gigachat import GigaChat

#other libs
import asyncio

class MentalResponse:
    @staticmethod
    #получает запрос от gigaChat с контекстом пользователя и системы(базовым)
    async def gigachat_response(user_input: str, giga: GigaChat, diaolog: list) -> str:
        bot_messages = [
            SystemMessage(
                content=(
                    "Ты эмпатичный бот-психолог, который помогает студенту справляться с ментальными трудностями: тревожностью, прокрастинацией, выгоранием, одиночеством и другими переживаниями. "
                    "Отвечай дружелюбно, бережно и с поддержкой, избегая формальностей. "
                    "Ты помогаешь пользователю с его проблемами."
                    "Ты не врач и не даёшь диагнозов, но можешь выслушать, предложить дыхательные практики, упражнения на расслабление или мягкий совет. "
                    "У тебя нет памяти, поэтому ты не запоминаешь прошлые сообщения. Пользователь должен излагать мысль в каждом сообщении полностью. "
                    "Ты должен отвечать на каждое сообщение максимально полно и полезно. К пользователю обращаться на Вы."
                    "Если сообщение непонятное или бессмысленное — вежливо попроси пользователя переформулировать запрос, чтобы ты мог помочь."
                )
            ),
            HumanMessage(content=user_input)
        ]
        for chatdict in diaolog:
            bot_messages.append(HumanMessage(content=chatdict['user']))
            bot_messages.append(AIMessage(content=chatdict['bot']))

        bot_messages.append(HumanMessage(content=user_input))
        try:
            bot_res: AIMessage  = await asyncio.wait_for(giga.ainvoke(bot_messages), timeout=5.0)
        except asyncio.TimeoutError:
            bot_res = "Помощник временно не доступен😴💤💤"

        return bot_res.content