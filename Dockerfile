FROM python:3.11-slim

LABEL maintainer="Georgy Lepsaya"
LABEL version="1.1"
LABEL description="Container for QCP-Omics"


RUN pip install --no-cache-dir qcp-omics


WORKDIR /app


ENTRYPOINT ["qcp"]

