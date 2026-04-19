from aiogram import Router, types
from aiogram.filters import Command, CommandStart

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Это бот с доступом к большой языковой модели по JWT-токену.\n"
        "Сначала отправьте токен командой: /token <JWT>\n"
        "Затем просто напишите вопрос и с удовольствием получите ответ."
    )


@router.message(Command("token"))
async def cmd_token(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /token <JWT>")
        return

    token = parts[1].strip()

    try:
        decode_and_validate(token)
    except ValueError:
        await message.answer("Токен невалиден или истёк. Получите новый в Auth Service.")
        return

    redis = get_redis()
    await redis.set(f"token:{message.from_user.id}", token)
    await message.answer("Токен сохранён. Теперь можно отправлять запросы модели.")


@router.message()
async def handle_text(message: types.Message):
    redis = get_redis()
    token = await redis.get(f"token:{message.from_user.id}")

    if not token:
        await message.answer(
            "У вас нет токена. Авторизуйтесь в Auth Service и отправьте токен командой /token <JWT>"
        )
        return

    try:
        decode_and_validate(token)
    except ValueError:
        await redis.delete(f"token:{message.from_user.id}")
        await message.answer(
            "Токен невалиден или истёк. Получите новый в Auth Service и отправьте командой /token <JWT>"
        )
        return

    llm_request.delay(message.chat.id, message.text)
    await message.answer("Запрос принят. Ответ придёт следующим сообщением.")
