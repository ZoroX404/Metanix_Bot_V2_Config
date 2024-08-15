FROM python:3.10
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt
# Install ffmpeg using apt
CMD ["python", "bot.py"]
