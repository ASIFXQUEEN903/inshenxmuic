FROM nikolaik/python-nodejs:python3.10-nodejs19

# Fix outdated buster sources
RUN sed -i 's|http://deb.debian.org/debian|http://deb.debian.org/debian bullseye main|' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://deb.debian.org/debian-security bullseye-security main|' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app/
RUN pip3 install --no-cache-dir -U -r requirements.txt

CMD bash start
