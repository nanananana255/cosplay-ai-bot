FROM nginx:alpine

# Установка certbot для Let's Encrypt
RUN apk add --no-cache certbot certbot-nginx

# Копируем конфигурацию
COPY nginx.conf /etc/nginx/nginx.conf
RUN mkdir -p /var/www/html /var/www/static /var/www/ton-connect

# Копируем манифест для TON Connect
COPY ton-connect-manifest.json /var/www/ton-connect/

# Скрипт для получения SSL сертификата
COPY init_ssl.sh /docker-entrypoint.d/
RUN chmod +x /docker-entrypoint.d/init_ssl.sh

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]