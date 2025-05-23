FROM node:22

WORKDIR /app

COPY ui/package*.json ./
RUN npm install

COPY ui/.env .env
COPY ui .

ENV HOST=0.0.0.0

CMD ["npm", "start"]