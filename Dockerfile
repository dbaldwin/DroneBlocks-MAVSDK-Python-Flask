FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update -y
RUN apt-get install -y \
    gcc \
    g++ \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN python -m pip install pip wheel --upgrade \
 && python -m pip install -r requirements.txt \
 && python -m pip install gunicorn
COPY . .

EXPOSE 8000

ENTRYPOINT ["gunicorn", "app:app", "-b", "0.0.0.0:8000"]
CMD []
