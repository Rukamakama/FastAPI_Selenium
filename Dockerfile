ARG PORT=443

FROM cypress/browsers:latest


RUN apt-get install python3 -y

RUN echo $(python3 -m site --user-base)


ENV PATH /home/root/.local/bin:${PATH}

RUN  apt-get update && apt-get install -y python3-pip
RUN mkdir home/app
WORKDIR home/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY templates ./templates
COPY main.py constants.py website_validation.py ./

CMD uvicorn main:app --host 0.0.0.0 --port 8000