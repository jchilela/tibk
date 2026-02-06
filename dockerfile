FROM python:3.10.12

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN apt-get update
RUN pip install -r requirements.txt
EXPOSE 8001
CMD python manage.py runserver 0.0.0.0:8001