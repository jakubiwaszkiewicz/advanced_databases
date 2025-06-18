FROM ubuntu:latest

# Instalacja systemowego Pythona, pip i venv
RUN apt-get update && apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Tworzymy i aktywujemy środowisko venv, instalujemy zależności
RUN python3 -m venv venv \
  && . venv/bin/activate \
  && venv/bin/pip install --no-cache-dir -r requirements.txt

# Eksponujemy port
EXPOSE 8000

# Używamy python/uvicorn z venv
CMD ["./venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
