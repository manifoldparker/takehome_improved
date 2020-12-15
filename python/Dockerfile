FROM python:3.8

COPY deploy.py /mnt/
COPY requirements.txt /mnt/
RUN pip install --upgrade pip
RUN pip install -r /mnt/requirements.txt



WORKDIR /mnt
