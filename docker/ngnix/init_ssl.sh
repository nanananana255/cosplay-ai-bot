#!/bin/sh

if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
    echo "Получение SSL сертификата для ${DOMAIN}..."
    certbot certonly --nginx -d ${DOMAIN} --non-interactive --agree-tos -m ${SSL_EMAIL}
fi

# Обновление конфига nginx с актуальными доменами
envsubst '${DOMAIN}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Запуск cron для автоматического обновления сертификатов
crond -b -L /var/log/cron.log

# Запуск основного процесса
exec "$@"