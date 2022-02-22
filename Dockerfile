FROM python:alpine

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/services/pydockerbackup/src

COPY Pipfile Pipfile.lock /opt/services/pydockerbackup/src/
WORKDIR /opt/services/pydockerbackup/src
RUN pip install pipenv && pipenv install --system

COPY . /opt/services/pydockerbackup/src

RUN mkdir /compressed && mkdir /backup

CMD ["python", "main.py"]