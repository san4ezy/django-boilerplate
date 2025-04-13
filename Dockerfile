FROM python:3.12-slim-bookworm

ARG ENV

ENV PROJECT_DIR "/app"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir $PROJECT_DIR
WORKDIR $PROJECT_DIR

RUN  apt-get update \
#  && apt-get install -y ... \
  && rm -rf /var/lib/apt/lists

COPY uv.lock pyproject.toml .

RUN  ls -l && pip install --upgrade pip \
  && pip install uv \
  && uv pip install --system -r pyproject.toml --group $ENV

ADD . $PROJECT_DIR
