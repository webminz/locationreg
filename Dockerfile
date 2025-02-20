FROM python:3.12
WORKDIR app
COPY . .
RUN apt update 
RUN apt install -y pipx
RUN pipx install poetry
RUN /root/.local/bin/poetry install 
CMD /root/.local/bin/poetry run fastapi dev locationreg/main.py
