FROM node:8

RUN apt-get update -y

COPY . /testcase-pybash
WORKDIR /testcase-pybash

EXPOSE 80

CMD ["node", "index.js"]