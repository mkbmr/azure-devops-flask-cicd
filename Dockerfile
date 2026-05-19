FROM python:3.13-alpine
LABEL maintainer="khalisilahk@gmail.com"
WORKDIR /mysite

# Leverage Docker layer caching for dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000
CMD ["python","flask_app.py"]
