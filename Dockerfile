FROM python:3.9-slim

RUN mkdir /app
WORKDIR /app

ADD ./src /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]