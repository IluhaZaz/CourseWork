FROM node:18-alpine

WORKDIR /front

COPY front/ .
RUN npm install --legacy-peer-deps

COPY . .

EXPOSE 4200

# Только для разработки! Не использовать в production
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--disable-host-check"]
