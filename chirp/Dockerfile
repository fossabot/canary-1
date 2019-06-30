FROM python:latest

WORKDIR /tmp/chirp

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=chirp.py
ENV AWS_SERVER_PUBLIC_KEY $AWS_SERVER_PUBLIC_KEY
ENV AWS_SERVER_SECRET_KEY $AWS_SERVER_SECRET_KEY

CMD ["flask", "run", "--host=0.0.0.0"]
