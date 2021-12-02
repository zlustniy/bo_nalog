FROM dc2.srvhub.tools/proxy/library/python:3.10.0

ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/Moscow

RUN apt-get update && \
    apt-get install -y \
    locales \
    poppler-utils \
    mc \
    && apt install -y ca-certificates \
    && sed -i '/^mozilla\/DST_Root_CA_X3.crt$/ s/^/!/' /etc/ca-certificates.conf \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY ./compose/django/default_locale /etc/default/locale
RUN chmod 0755 /etc/default/locale

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure -f noninteractive locales

COPY ./compose/django/wait /
COPY ./.coveragerc ./
WORKDIR /webapp

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./compose/django/requirements /requirements
ENV PATH /webapp/.venv/bin:$PATH
RUN pip install -r /requirements/poetry.txt --no-cache-dir \
 && poetry config virtualenvs.in-project true

COPY ./pyproject.toml ./poetry.lock ./

RUN poetry install \
 && pip install -r /requirements/gunicorn.txt --no-cache-dir \
 && pip install -r /requirements/deploy.txt --no-cache-dir

COPY ./src /webapp
COPY ./compose/django/commands /commands
COPY ./compose/django/entrypoint.sh /entrypoint.sh

RUN groupadd -r django \
    && useradd -r -u 1500 -g django django \
    && chmod +x /entrypoint.sh \
    && chown django /entrypoint.sh \
    && chmod -R +x /commands \
    && mkdir -p /webapp/logs \
    && chown -R django /commands \
    && chown -R django /webapp \
    && chmod +x /wait

USER 1500

ARG buildno
ARG build_datetime
ARG commit
ENV VERSION ${buildno}
ENV BUILD_TIME ${build_datetime}
ENV COMMIT ${commit}

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn"]