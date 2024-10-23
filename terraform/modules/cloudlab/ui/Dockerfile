FROM python:3.11-buster
LABEL author=egawrieh@google.com
COPY . cloudlab/
WORKDIR cloudlab
RUN apt-get update
RUN pip install -r requirements.txt
CMD  ["python", "main.py"]
