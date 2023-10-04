FROM python:3.11.4

RUN mkdir /app

WORKDIR /app/src
COPY ./ /app/src
RUN pip install -r requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/src/vits-tts-vi.json

ENTRYPOINT ./start.sh
# CMD ["python","-u","server.py"]
