FROM node:18-alpine AS build

WORKDIR /app
COPY front/ .
RUN npm ci --legacy-peer-deps
RUN npm run build -- --configuration production

FROM nginx:alpine
COPY --from=build /app/dist/to_do_list/browser /usr/share/nginx/html

RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
