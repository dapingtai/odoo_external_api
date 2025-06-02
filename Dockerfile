FROM python:3.12.4

RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade --proxy http://IG1819:3ZTCi6eb@10.36.6.66:3128 -r /code/requirements.txt

COPY . /code

CMD ["python", "run.py"]