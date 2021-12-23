FROM python:latest
COPY Code.py /
ARG my_secret_token
ENV my_token $my_secret_token
RUN pip install --user pyTelegramBotAPI
CMD ["python3", "Code.py"]
