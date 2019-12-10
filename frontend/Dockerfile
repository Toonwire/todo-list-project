FROM node:13.1.0-alpine 

#ENV NODE_PATH=/node_modules
#ENV PATH=$PATH:/node_modules/.bin

WORKDIR /usr/src/app

COPY ./todo-list-app/package*.json ./
# install dependencies into node_modules/ directory
RUN npm install

COPY ./todo-list-app .

EXPOSE 3000
CMD npm start


