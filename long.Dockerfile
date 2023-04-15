ARG PORT=443

FROM --platform=linux/amd64  python:3.11.2

# Use the official Python 3 image as the base image
FROM python:3

# Install required packages for Chrome and Chromedriver
RUN apt-get update && apt-get install -yq \
    wget \
    gnupg2 \
    unzip \
    libgconf-2-4 \
    libncurses5 \
    libsqlite3-dev \
    libssl-dev \
    libnss3 \
    libasound2 \
    libxss1 \
    libxtst6 \
    xvfb \
    libgbm1 \
    libfontconfig1 \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16 \
    libx11-6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add the Google Chrome repository's signing key
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Add the Google Chrome repository to the sources list
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list

# Install Google Chrome stable version
RUN apt-get update && apt-get install -yq \
    google-chrome-stable=112.0.5615.121-1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
ENV CHROME_PATH=/usr/bin/google-chrome-stable

# Download and install Chromedriver
RUN wget https://chromedriver.storage.googleapis.com/112.0.5615.28/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && chmod +x chromedriver \
    && mv chromedriver /usr/local/bin/

# Set the display port to avoid crash
ENV DISPLAY=:99

RUN mkdir home/app
WORKDIR home/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY templates ./templates
COPY main.py constants.py website_validation.py ./

CMD uvicorn main:app --host 0.0.0.0 --port 8000 --reload
