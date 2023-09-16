FROM python:3.8-slim

WORKDIR /project

COPY . /project

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "backend/app.py"]
