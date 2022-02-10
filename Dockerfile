FROM node:17 AS builder
LABEL maintainer="bakedSpaceTime"

# TODO: copy package.json and package-lock.json to leverage Docker cache
COPY ./frontend/ /frontend/
RUN mkdir /frontend/public/static/

WORKDIR /frontend
RUN npm install
RUN npm run prepare
RUN npm run build


FROM ubuntu:20.04

RUN apt-get update -y && apt-get install -y python3 python3-pip curl apt-utils
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install nginx

# Copy just the requirements.txt to leverage Docker cache
COPY ./backend/requirements.txt /backend/requirements.txt
WORKDIR /backend
RUN pip3 install -r requirements.txt

COPY ./backend /backend
COPY --from=builder /frontend/public /frontend

COPY ./docker-files/default /etc/nginx/sites-available/default

COPY ./docker-files/start.sh /start.sh

CMD [  "bash","/start.sh" ]
