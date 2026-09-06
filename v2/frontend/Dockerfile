FROM node:22-alpine

ENV TZ=Europe/Moscow \
    NODE_ENV=development \
    NEXT_TELEMETRY_DISABLED=1

RUN apk add --no-cache libc6-compat tzdata \
    && cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo Europe/Moscow > /etc/timezone

WORKDIR /app

# Tree may only have README until the Next app exists. Runtime bind-mounts overlay /app.
COPY . /app

EXPOSE 3000

# Compose overrides this for the local slice (npm install + next dev).
CMD ["sh", "-c", "if [ -f package.json ]; then npm install && exec npm run dev -- -H 0.0.0.0 -p 3000; else node -e \"require('http').createServer((_,r)=>{r.writeHead(503);r.end('frontend app not present')}).listen(3000)\"; fi"]
