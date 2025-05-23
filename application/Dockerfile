FROM python:3.13

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY .env ./
COPY client_secret.json ./
COPY token.json ./
COPY ./application /app/application

CMD ["uvicorn", "application.main:application", "--host", "0.0.0.0", "--port", "8000"]