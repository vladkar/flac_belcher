# Use a minimal Python image.
FROM python:3.12-slim

# Install ffmpeg and libmagic-dev (without fixed version constraints).
RUN apt-get update && \
    apt-get install -y ffmpeg libmagic-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory.
WORKDIR /app

# Copy the requirements.txt from the root and install dependencies.
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code from the src folder into the container.
COPY src/ /app/

# Set environment variables (these can be overridden by docker-compose).
ENV FFMPEG_PATH=ffmpeg
ENV DIR_IN=/music/in
ENV DIR_OUT=/music/out
ENV DRY_RUN=false
ENV HIDE_FFMPEG_LOGS=true

# Run the main.py script.
CMD ["python", "main.py"]
