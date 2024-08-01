FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV AWS_DEFAULT_REGION=eu-west-1

EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]