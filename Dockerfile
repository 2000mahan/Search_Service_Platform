FROM python:3.6-alpine AS build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN python3 -m pip install --upgrade pip
RUN pip3 install python-dateutil
RUN apk --no-cache add --virtual .builddeps gcc gfortran musl-dev     && pip install numpy==1.14.0     && apk del .builddeps     && rm -rf /root/.cache


COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt


FROM python:3.6-alpine AS target
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

ENV ENV_FILE=/env/.env

EXPOSE 8080

COPY /app .
CMD ["python", "app.py"]
