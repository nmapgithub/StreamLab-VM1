FROM python:3.9-slim
WORKDIR /app
COPY manage/app.py /app/
COPY manage/static /app/static
RUN pip install --no-cache-dir flask
EXPOSE 5000
CMD ["python", "app.py"]
