
FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1

RUN  apk add --no-cache --virtual build-deps gcc python3-dev musl-dev git openssh-client && \
apk add --no-cache postgresql-dev jpeg-dev zlib-dev \
freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
&& apk add libffi-dev py-cffi

RUN addgroup -S accounting \
    && adduser -S -G accounting accounting


# Requirements are installed here to ensure they will be cached.
COPY ./ssh /root/.ssh
RUN chmod -R 600 /root/.ssh/
ENV GIT_SSH_COMMAND="ssh -i /root/.ssh/id_rsa"
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements && rm -rf /root/.ssh

RUN apk del build-deps

COPY ./compose/production/accounting/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint
RUN chown accounting /entrypoint

COPY ./compose/production/accounting/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
RUN chown accounting /start
COPY . /app

RUN chown -R accounting /app

USER accounting

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
