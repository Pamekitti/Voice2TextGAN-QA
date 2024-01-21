FROM python:3.9-slim-buster

WORKDIR /main

COPY AltoGPT/qa_module/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]