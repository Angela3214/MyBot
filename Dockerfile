FROM python:latest
COPY main.py /
ARG my_secret_token
ENV my_token $my_secret_token
RUN pip install --user pyTelegramBotAPI
CMD ["python3", "Code.py"]
