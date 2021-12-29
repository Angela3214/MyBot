FROM python:latest
COPY main.py /
ARG my_secret_token
ENV my_token $my_secret_token
RUN pip install --user -r requirements.txt
CMD ["python3", "main.py"]
