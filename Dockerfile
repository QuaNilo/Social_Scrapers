FROM python:3.11

WORKDIR /app

RUN apt-get update

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get -y update

# Magic happens
RUN apt-get install -y google-chrome-stable



#install python dependencies
COPY requirements.txt /app/

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt

#copy local files
# Use your Gunicorn configuration file


COPY . /app/

CMD ["gunicorn", "--config", "gunicorn_config.py", "main:app"]
