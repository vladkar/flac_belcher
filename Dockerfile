# Use a minimal Python image.
FROM python:3.12-slim

# Install ffmpeg and libmagic-dev without fixed version constraints.
RUN apt-get update && \
    apt-get install -y ffmpeg libmagic-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory.
WORKDIR /app

# Copy all project files into the container so that the 'src' folder is preserved.
COPY . /app/

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (these can be overridden by docker-compose).
ENV FFMPEG_PATH=ffmpeg
ENV DIR_IN=/music/in
ENV DIR_OUT=/music/out
ENV DRY_RUN=false
ENV HIDE_FFMPEG_LOGS=true

# Set the working directory.
WORKDIR /app/src

# Run the main.py script from the src folder.
CMD ["python", "main.py"]
