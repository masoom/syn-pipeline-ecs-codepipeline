FROM python:3.8-slim

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY . /dir
WORKDIR /dir

CMD ["python", "main.py"]