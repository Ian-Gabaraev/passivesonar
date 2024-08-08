# Dockerfile
# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /server

# Install system dependencies for building Python packages
RUN apt-get update && \
    apt-get install -y gcc libasound2-dev portaudio19-dev python3-dev ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the image
COPY requirements.txt /server/

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the image
COPY . /server/

# Set the default command to run the remaining processes
CMD ["sh", "-c", "python ws_server.py & python ws_relay_from_redis.py"]