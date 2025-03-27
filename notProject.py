import asyncio
from bs4 import BeautifulSoup
import httpx

#Случайная шутка
class JokeGenerator:
    @staticmethod
    async def randomJoke() -> str:
        url = f"https://www.anekdot.ru/random/anekdot/"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                topicboxes = soup.find("div", class_="topicbox", attrs={"data-t": "j"})
                joke_text = topicboxes.find("div", class_="text").text.strip()

                return joke_text
            else:
                return "Сегодня шуток не будет (ﾉಥ益ಥ）ﾉ  ┻━┻"