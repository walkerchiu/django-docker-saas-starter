###########
# BUILDER #
###########

# Pull official base image
FROM python:3.11.0-slim AS builder

# Set work directory
WORKDIR /usr/src/app

# Install psycopg2 dependencies
RUN apt-get update \
    && apt-get -y install postgresql-server-dev-all gcc python3-dev musl-dev libpq-dev

# Install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########

# From builder
FROM builder AS final

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--preload", "--workers", "3", "app.wsgi:application"]
