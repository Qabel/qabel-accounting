FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache --virtual build-deps python3-dev musl-dev gcc git openssh-client && \
apk add --no-cache postgresql-dev jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  # CFFI dependencies
  && apk add  --no-cache libffi-dev py-cffi \
  # Translations dependencies
  && apk add --no-cache  gettext

# Requirements are installed here to ensure they will be cached.
COPY ./ssh /root/.ssh
RUN chmod -R 600 /root/.ssh/
ENV GIT_SSH_COMMAND="ssh -i /root/.ssh/id_rsa"
COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt


COPY ./compose/production/accounting/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/accounting/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
