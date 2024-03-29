FROM python:3.11-slim

COPY . .
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.in-project true && \
    poetry install

USER nobody

CMD poetry run python server.py
