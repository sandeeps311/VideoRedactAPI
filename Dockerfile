FROM python:3.7

ADD requirements.txt /app/requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
RUN pip install -r /app/requirements.txt


EXPOSE 80

ADD ./app 

CMD ["uvicorn", "App:app", "--host", "0.0.0.0", "--port", "80"]
