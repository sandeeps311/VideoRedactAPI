FROM python:3.8

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt


EXPOSE 80

ADD ./app 

CMD ["uvicorn", "App:app", "--host", "0.0.0.0", "--port", "80"]
