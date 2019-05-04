FROM python:latest

WORKDIR /tmp/chirp

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=chirp.py

CMD ["flask", "run", "--host=0.0.0.0"]
