FROM python:latest

WORKDIR /tmp/silence

COPY ./requirements.txt .

RUN pip install -r requirements.txt

ENV TWILIO_ACCOUNT_ID $TWILIO_ACCOUNT_ID
ENV TWILIO_AUTH_TOKEN $TWILIO_AUTH_TOKEN

COPY . .

CMD ["python", "-u", "silence.py"]
