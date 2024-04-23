FROM python:3.10
COPY app /app
WORKDIR /app
RUN pip install -r requriements.txt
CMD ["pyhon", "app.py"]

