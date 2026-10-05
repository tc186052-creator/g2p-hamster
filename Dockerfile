# g2p-hamster — HTTP API server
# Build:  docker build -t g2p-hamster .
# Run:    docker run -p 8080:8080 g2p-hamster
# Dùng:   curl -s localhost:8080/g2p -d '{"text":"HLV của HAGL họp HĐQT tại TP.HCM."}'
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends espeak-ng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .

EXPOSE 8080
CMD ["python3", "-m", "g2p_hamster.serve", "--host", "0.0.0.0", "--port", "8080"]
