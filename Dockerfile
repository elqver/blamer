FROM python:3.12
COPY app /app
WORKDIR /app
RUN ls
RUN pip install -r requirements.txt
CMD ["python", "app.py"]