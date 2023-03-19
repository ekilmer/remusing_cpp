FROM python:3

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y parallel \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY remusing_cpp ./remusing_cpp

RUN pip install --no-cache-dir . && \
    python -m remusing_cpp --init

WORKDIR /workspace

CMD ["python", "-m", "remusing_cpp"]
