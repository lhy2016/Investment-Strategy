FROM python:3.7
RUN mkdir /invest
WORKDIR /invest
ENV FLASK_APP = app.py
COPY requirements.txt /invest/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt