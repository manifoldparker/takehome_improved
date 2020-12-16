FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY deploy.py /app/
COPY main.py /app/
COPY requirements.txt /mnt/
RUN pip install --upgrade pip
RUN pip install -r /mnt/requirements.txt