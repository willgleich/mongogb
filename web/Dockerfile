FROM python:latest
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]
#ENTRYPOINT ["gunicorn"]
#CMD ["-b", "0.0.0.0:5000", "wsgi:app", "--reload"]