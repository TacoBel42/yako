FROM python:3.10-bullseye

RUN curl -sSL https://install.python-poetry.org | python -
COPY ./ ./
ENV PATH="/root/.local/bin:$PATH"
RUN poetry install
