FROM python:3.12-alpine
RUN addgroup -g 1000 app
RUN adduser -G app -D -u 1000 -h /app app
WORKDIR /app
USER app
COPY dist .
RUN pip install locationreg-0.1.0-py3-none-any.whl
CMD ["python", "-m", "locationreg.main"]

