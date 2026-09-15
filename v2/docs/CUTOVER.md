# Cutover — V2 на ВМ и домен sol-chef.ru

Операционный чеклист. Стек не меняет: [ARCHITECTURE.md](ARCHITECTURE.md), числа — [DEFAULTS.md](DEFAULTS.md).

Сейчас V1 больше не корень репозитория: статический сайт лежит в [`archive/v1/`](../../archive/v1/). Живой сайт — Compose в `v2/infra`. Next и Django **не** переезжают в корень.

**Не пушить `main`, пока V2 не отвечает на домене.** В корне больше нет `index.html` и `CNAME`: GitHub Pages после такого push перестанет отдавать текущий sol-chef.ru.

## Что меняется

| Сейчас | После |
|--------|--------|
| GitHub Pages отдаёт статический V1 с `sol-chef.ru` | ВМ (Timeweb, РФ) отдаёт V2: Caddy → Next + Django + Postgres |
| DNS A-записи на IP GitHub Pages (`185.199.108–111.153`) | те же имена (`sol-chef.ru`, при желании `www`) на IP ВМ |
| Каталог = JSON в корне | каталог = Postgres (дамп с локального Compose, **не** голый `import_v1`) |

`import_v1` поднимает только старые 43 карточки из архива и затрёт оверлеи. В локальной БД уже ~135 рецептов и два набора «На неделю». Их нужно перенести дампом.

Реестр образов (HUMAN 7.7) ещё «позже»: первый запуск собирает образы **на ВМ**. Позже — CI `pull`, без `build` на VPS.

## 0. На домашней машине

Compose с данными должен быть жив (`docker compose -f v2/infra/docker-compose.yml up`).

1. Дамп каталога (файл не коммитить):

```powershell
docker compose -f v2/infra/docker-compose.yml exec -T postgres pg_dump -U solchef -d solchef --clean --if-exists > v2/infra/solchef.dump
```

2. Секретный ключ Django и пароль БД придумайте новые. Локальный `DJANGO_SECRET_KEY` из среза в прод не копировать.

3. Хеш пароля на `/admin/` (Caddy, поверх логина Django):

```powershell
docker run --rm caddy:2-alpine caddy hash-password --plaintext "ВАШ_ПАРОЛЬ"
```

В `.env` каждый `$` в хеше удвоить: `$2a$14$…` → `$$2a$$14$$…`. Иначе Compose съест переменные.

## 1. ВМ Timeweb

Ориентир: Ubuntu 24.04, **8 ГБ RAM**, диск от 40 ГБ, регион РФ. В панели откройте порты **22, 80, 443**. Postgres/Redis/8000/3000 наружу не публиковать.

SSH:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
# выйти из SSH и зайти снова
```

Swap 4 ГБ:

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo timedatectl set-timezone Europe/Moscow
```

Код на ВМ — пока без push в `main`:

- либо `scp`/архив с этой машины,
- либо ветка не `main` (Pages смотрит `main` / корень).

```bash
sudo mkdir -p /opt/sol-chef
sudo chown "$USER":"$USER" /opt/sol-chef
# пример: git clone -b v2-cutover git@github.com:AterDeus/sol-chief.git /opt/sol-chef
cd /opt/sol-chef
```

Положите `v2/infra/solchef.dump` на ВМ (scp). Не в git.

```bash
cd /opt/sol-chef/v2/infra
cp .env.example .env
nano .env
```

Обязательно замените `CHANGE_ME`: `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD`, `ACME_EMAIL`, `ADMIN_BASIC_USER`, `ADMIN_BASIC_HASH`. Для первого запуска оставьте `CADDYFILE=./Caddyfile.http`.

В `DJANGO_ALLOWED_HOSTS` оставьте `backend,localhost,127.0.0.1` (healthcheck) и **добавьте публичный IP ВМ**, пока заходите по IP. После DNS IP можно убрать.

Почта `ACME_EMAIL` — для Let's Encrypt; это не вход на сайт (аккаунты — следующий релиз, HUMAN 10.13).

## 2. Поднять стек и залить БД

```bash
cd /opt/sol-chef/v2/infra
docker compose -f docker-compose.prod.yml --env-file .env up -d postgres redis
# дождаться healthy
docker compose -f docker-compose.prod.yml --env-file .env exec -T postgres \
  psql -U solchef -d solchef < solchef.dump

docker compose -f docker-compose.prod.yml --env-file .env up -d --build
docker compose -f docker-compose.prod.yml --env-file .env ps
curl -fsS "http://127.0.0.1/healthz"
```

Снаружи: `http://<IP_ВМ>/` — витрина, `/recipes`, `/prep`, `/tips`. Старый URL ` /recipe.html?id=<slug>` должен уводить на `/recipes/<slug>`.

Если фронт не собрался: `docker compose -f docker-compose.prod.yml --env-file .env logs frontend`.

Суперпользователь Django, если его не было в дампе:

```bash
docker compose -f docker-compose.prod.yml --env-file .env exec backend \
  uv run python manage.py createsuperuser
```

`/admin/` закрыт basic auth Caddy **и** логином Django.

## 3. Домен: с GitHub Pages на ВМ

Сейчас у регистратора (как в архивном V1 PLAN):

- A: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
- при наличии www: CNAME `www` → `AterDeus.github.io` (или ваш github.io)

Сделайте так:

1. В панели Timeweb скопируйте **публичный IPv4** ВМ.
2. У регистратора **удалите** все A (и AAAA, если есть) GitHub Pages.
3. Добавьте **A** `sol-chef.ru` → IP ВМ.
4. `www`: либо A на тот же IP, либо CNAME на `sol-chef.ru`.
5. Если TTL был сутки — смена может идти часами. Перед окном лучше снизить TTL заранее.

Проверка, не с вашего кэша:

```bash
nslookup sol-chef.ru 8.8.8.8
```

Должен быть IP ВМ, не `185.199.*`.

Пока DNS не дошёл, Caddy **не** сможет выписать сертификат. Не переключайте `CADDYFILE` раньше времени.

## 4. HTTPS

Когда `nslookup` уже показывает ВМ:

```bash
cd /opt/sol-chef/v2/infra
# в .env:
# CADDYFILE=./Caddyfile.prod
# DJANGO_CSRF_TRUSTED_ORIGINS=https://sol-chef.ru,https://www.sol-chef.ru
docker compose -f docker-compose.prod.yml --env-file .env up -d caddy
docker compose -f docker-compose.prod.yml --env-file .env logs caddy
```

Откройте `https://sol-chef.ru`. Сертификат — Let's Encrypt через Caddy, отдельно ничего покупать не нужно.

## 5. Выключить GitHub Pages

1. GitHub → репозиторий → **Settings → Pages → Disable** (или Source: None).
2. Custom domain очистить, если поле ещё заполнено.
3. Файл `CNAME` в архиве (`archive/v1/CNAME`) больше не у корня — так и должно быть.
4. После того как `https://sol-chef.ru` открывает **V2**, можно пушить `main` с архивом V1.

Пока Pages включён и DNS ещё на GitHub — в проде останется V1. Пока DNS на ВМ, а Pages ещё жив — Pages просто перестанет получать запросы, это нормально.

## 6. Обновления после cutover

Пока нет реестра образов:

```bash
cd /opt/sol-chef
git pull
cd v2/infra
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

`next build` на хосте ВМ не запускать — сборка только внутри Docker. На хосте не публиковать порты backend/frontend.

Бэкап (DEFAULTS: сутки, 7 дней, не тот бакет что медиа — медиа пока нет):

```bash
docker compose -f docker-compose.prod.yml --env-file .env exec -T postgres \
  pg_dump -U solchef -d solchef | gzip > /opt/sol-chef/backups/solchef-$(date +%F).sql.gz
```

## Если что-то не так

| Симптом | Что проверить |
|---------|----------------|
| GitHub Pages после push отдаёт README | вы пушнули до переключения DNS; верните Pages или ускорьте A-записи |
| Caddy: ACME error / NXDOMAIN | DNS ещё не на ВМ; держите `Caddyfile.http` |
| 502 на `/` | `docker compose … ps` — frontend/backend healthy? |
| `/admin/` 401 без формы Django | basic auth Caddy; хеш с удвоенными `$` в `.env` |
| Пустой каталог / 43 карточки | залили не тот дамп или прогнали `import_v1` на проде |
| CSRF на https | `DJANGO_CSRF_TRUSTED_ORIGINS` с `https://sol-chef.ru` |

Откат на V1 (только если DNS ещё можно вернуть на GitHub): снова A-записи `185.199.108–111.153`, включить Pages, branch `main` / root — и **не** пушить коммит без корневого `index.html`. После cutover откат = отдельное решение, архивный V1 сам по себе домен не обслуживает.
