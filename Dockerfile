FROM python:3.8

WORKDIR /app

# Copy All files to the container
COPY . .

# Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV AWS_DEFAULT_REGION=eu-west-1

# Port number the container should expose
EXPOSE 5000

# Run command on boot
CMD ["python", "./app.py"]