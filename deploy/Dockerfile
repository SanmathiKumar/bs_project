FROM python:3.9.6-slim-buster

ENV BS_CUSTOM_MODEL_SERVICE_RELOAD="True"
ENV BS_CUSTOM_MODEL_SERVICE_PORT="8000"
ENV BS_CUSTOM_MODEL_SERVICE_ENVIRONMENT="prod"
ENV BS_CUSTOM_MODEL_SERVICE_HOST=0.0.0.0

RUN pip install poetry==1.2.2

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Installing requirements
RUN poetry install

# Copying actuall application
COPY . /app/src/
RUN poetry install

CMD ["/usr/local/bin/python", "-m", "bs_custom_model_service"]
