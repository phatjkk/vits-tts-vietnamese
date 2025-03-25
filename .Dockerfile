FROM python:3.11.4

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Create application directory
RUN mkdir /app

# Set the working directory
WORKDIR /app/src
COPY requirements.txt .


# Install the application dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the application source code to the container
COPY ./ /app/src


# Set environment variable for the application
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/src/vits-tts-vi.json

# Set the entrypoint script
ENTRYPOINT ./start.sh
# CMD ["python", "-u", "server.py"]