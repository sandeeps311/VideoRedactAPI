FROM python:3.7

ADD requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

EXPOSE 80

COPY ./app /app

CMD ["uvicorn", "app.online_classes:app", "--host", "0.0.0.0", "--port", "80"]
