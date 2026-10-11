FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY project ./project
RUN pip install --no-cache-dir .

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "project.verify"]