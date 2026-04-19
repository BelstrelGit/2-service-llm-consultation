FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .
COPY .env .
RUN uv sync

COPY . .

CMD ["uv", "run", "python", "-m", "app.bot.dispatcher"]
