FROM python:3.8-slim-buster

WORKDIR /app

# Copy All files to the container
COPY . .

# Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV AWS_DEFAULT_REGION=eu-west-1
ENV FLASK_APP=app.py

# Port number the container should expose
EXPOSE 5000

# Run command on boot
CMD ["flask", "run", "--host", "0.0.0.0"]