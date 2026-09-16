FROM node:22-alpine

ENV TZ=Europe/Moscow \
    NODE_ENV=development \
    NEXT_TELEMETRY_DISABLED=1

RUN apk add --no-cache libc6-compat tzdata \
    && cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo Europe/Moscow > /etc/timezone

WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --no-audit --no-fund

# Bind-mount at runtime overlays /app; empty node_modules volume is seeded from this layer.
COPY . /app

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]
