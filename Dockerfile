FROM python:3.7

ADD requirements.txt /app/requirements.txt
RUN set -x \
    && add-apt-repository ppa:mc3man/trusty-media \
    && apt-get update \
    && apt-get dist-upgrade \
    && apt-get install -y --no-install-recommends \
        ffmpeg \ 
RUN pip install -r /app/requirements.txt


EXPOSE 80

ADD ./app 

CMD ["uvicorn", "App:app", "--host", "0.0.0.0", "--port", "80"]
