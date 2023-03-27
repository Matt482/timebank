FROM python:3.11
EXPOSE 5000
WORKDIR /python-docker
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=run.py
CMD ["flask", "run", "--host", "0.0.0.0"]
