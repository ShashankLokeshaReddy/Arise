# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY ./django_prototype /code/django_prototype
COPY ./arise_prototype /code/arise_prototype/arise_prototype
COPY setup.py /code/arise_prototype/
RUN pip install ./arise_prototype

# Existing code in your Dockerfile...

# Install ODBC driver and dependencies
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    tdsodbc

# Install SQL Server ODBC driver
RUN apt-get install -y gnupg2
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Install pyodbc
RUN pip install pyodbc

# Configure ODBC data source
# RUN echo "[YourDataSourceName]" >> /etc/odbc.ini
# RUN echo "Driver=ODBC Driver 17 for SQL Server" >> /etc/odbc.ini
# RUN echo "Server=192.168.1.9" >> /etc/odbc.ini
# RUN echo "Database=schulte_copy" >> /etc/odbc.ini
# RUN echo "UID=ARISE" >> /etc/odbc.ini
# RUN echo "PWD=4FbC2zF2" >> /etc/odbc.ini

# Continue with the rest of your Dockerfile...
