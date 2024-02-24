FROM python:3.11.7
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]

