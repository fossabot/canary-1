FROM python:latest

WORKDIR /tmp/silence

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "silence.py"]
