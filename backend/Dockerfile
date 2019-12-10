FROM python:3.7.5-alpine3.10

WORKDIR /usr/src/app
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./server .
EXPOSE 5000
CMD python -u ./todo_service.py