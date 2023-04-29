FROM python:3.10

WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ADD . /app

EXPOSE 5000

# migrate and runserver
CMD ["sh", "-c", "flask db upgrade && python app.py"]
