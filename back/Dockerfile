FROM python:3.10

RUN mkdir /app

WORKDIR /back

COPY ../requirements.txt .

COPY back/src ./src
COPY ../migrations ./migrations
COPY ../alembic.ini .

RUN pip install -r requirements.txt

COPY .. .