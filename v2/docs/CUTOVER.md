# Cutover — V2 на ВМ и домен sol-chef.ru

Операционный чеклист дня релиза. Стек не меняет: [ARCHITECTURE.md](ARCHITECTURE.md), числа — [DEFAULTS.md](DEFAULTS.md).

**Next и Django в корень не переносить.** Они остаются в `v2/`. Статический V1 уже лежит в [`archive/v1/`](../../archive/v1/). Корень репозитория — монорепо, не сайт.

## Где что сейчас

| Где | Что |
|-----|-----|
| Эта машина, папка `v2/` | Живое приложение 2.0 (Next + Django + Postgres) |
| Эта машина, `archive/v1/` | Архив старого сайта. Не прод |
| Локальный git `main` | Уже монорепо (V1 в архиве). **Не пушить в `origin/main`** |
| GitHub `origin/main` | Ещё старый корень с `index.html` / `CNAME` — отсюда GitHub Pages кормит домен |
| DNS `sol-chef.ru` | A-записи GitHub Pages `185.199.108–111.153` |
| Локальная БД | ~135 рецептов и два набора «На неделю». На прод — **дамп**, не `import_v1` |

`import_v1` поднимает только старые 43 карточки из архива и затрёт оверлеи. Реестра образов нет (HUMAN 7.7 «позже»): первый запуск **собирает образы на ВМ**. Позже — CI `pull`, без `build` на VPS.

**Порядок не ломать:** сначала V2 отвечает по IP ВМ → потом DNS → потом HTTPS → потом выключить Pages → **только тогда** пушить `main`. Иначе Pages останется без `index.html` и домен умрёт, пока DNS не дошёл.

## 0. На домашней машине

Compose с данными должен быть жив хотя бы на Postgres:

```powershell
docker compose -f v2/infra/docker-compose.yml ps
```

### 0.1. Дамп каталога

Файл **не коммитить** (`v2/infra/.gitignore`: `*.dump`). На Windows не используйте `>` из PowerShell — он портит кодировку. Через `cmd`:

```bat
cmd /c "docker compose -f v2/infra/docker-compose.yml exec -T postgres pg_dump -U solchef -d solchef --clean --if-exists --no-owner --no-acl --encoding=UTF8 > v2\infra\solchef.dump"
```

Ожидаемый размер порядка **3 МБ**. Первые строки: `PostgreSQL database dump`, `SET client_encoding = 'UTF8'`.

Снимок от 2026-09-18 лежит в `v2/infra/solchef.dump` (135 карточек, наборы `nedelya-sentyabrskaya-spokoynaya` и `nedelya-kapusta-i-volokna`). Перед повторным дампом, если правили JSON набора и хотите эти фразы в проде:

```powershell
docker compose -f v2/infra/docker-compose.yml exec backend uv run python manage.py import_prep_kit --path /v2-docs/drafts/weekly-prep/nedelya-sentyabrskaya-spokoynaya.json
```

Нужен запущенный `backend`, не только Postgres.

### 0.2. Секреты

Придумайте **новые**, локальный срез в прод не копировать:

- `DJANGO_SECRET_KEY` — длинная случайная строка
- `POSTGRES_PASSWORD` — пароль роли `solchef`
- `ACME_EMAIL` — ваша почта для Let's Encrypt (это не вход на сайт)
- пароль basic auth на `/admin/`

Хеш пароля Caddy:

```powershell
docker run --rm caddy:2-alpine caddy hash-password --plaintext "ВАШ_ПАРОЛЬ"
```

В `.env` каждый `$` в хеше удвоить: `$2a$14$…` → `$$2a$$14$$…`. Иначе Compose съест переменные.

### 0.3. Код на ВМ — без push в `main`

GitHub Pages смотрит на `origin/main` / корень. Локальный `main` уже без `index.html`. Варианты:

**А. Ветка не `main` (удобно потом `git pull`):**

```powershell
git checkout -b v2-cutover
git push -u origin v2-cutover
```

На ВМ: `git clone -b v2-cutover git@github.com:AterDeus/sol-chief.git /opt/sol-chef`

**Б. Копия без GitHub** (если ветку пушить не хотите):

```powershell
tar --exclude=node_modules --exclude=.next --exclude=__pycache__ --exclude=.git -cvf sol-chef-v2.tar v2 archive AGENTS.md README.md LICENSE
scp sol-chef-v2.tar USER@IP_ВМ:/tmp/
```

Дамп отдельно:

```powershell
scp v2\infra\solchef.dump USER@IP_ВМ:/tmp/solchef.dump
```

`USER` и `IP_ВМ` — ваши. Файл дампа в git не класть.

## 1. ВМ (Docker уже есть)

Ориентир: Ubuntu, **8 ГБ RAM**, диск от 40 ГБ, регион РФ (HUMAN 7.3–7.4: Timeweb). В панели откройте порты **22, 80, 443**. Postgres, Redis, 8000, 3000 **наружу не публиковать**.

Если Docker уже установлен, установку пропускайте. Проверьте:

```bash
docker --version
docker compose version
id   # в группе docker? если нет: sudo usermod -aG docker "$USER" и перелогин
```

Swap 4 ГБ, если ещё нет (сборка Next на ВМ иначе может упереться в RAM):

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo timedatectl set-timezone Europe/Moscow
```

Код:

```bash
sudo mkdir -p /opt/sol-chef /opt/sol-chef/backups
sudo chown "$USER":"$USER" /opt/sol-chef
# либо clone ветки v2-cutover, либо распаковать tar в /opt/sol-chef
cd /opt/sol-chef
cp /tmp/solchef.dump v2/infra/solchef.dump
```

```bash
cd /opt/sol-chef/v2/infra
cp .env.example .env
nano .env
```

Обязательно замените все `CHANGE_ME`: `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD`, `ACME_EMAIL`, `ADMIN_BASIC_USER`, `ADMIN_BASIC_HASH`. Для первого запуска:

```
CADDYFILE=./Caddyfile.http
DJANGO_ALLOWED_HOSTS=backend,localhost,127.0.0.1,<ПУБЛИЧНЫЙ_IP_ВМ>
DJANGO_CSRF_TRUSTED_ORIGINS=http://<ПУБЛИЧНЫЙ_IP_ВМ>
```

После DNS IP из `ALLOWED_HOSTS` можно убрать; CSRF станет `https://sol-chef.ru`.

## 2. Поднять стек и залить БД

```bash
cd /opt/sol-chef/v2/infra
docker compose -f docker-compose.prod.yml --env-file .env up -d postgres redis
# дождаться healthy
docker compose -f docker-compose.prod.yml --env-file .env ps
```

Восстановление (тот же образ Postgres 16, что в compose):

```bash
docker compose -f docker-compose.prod.yml --env-file .env exec -T postgres \
  psql -U solchef -d solchef < solchef.dump
```

Проверка, что это не 43 карточки V1:

```bash
docker compose -f docker-compose.prod.yml --env-file .env exec postgres \
  psql -U solchef -d solchef -c "SELECT count(*) FROM recipes_recipe;"
docker compose -f docker-compose.prod.yml --env-file .env exec postgres \
  psql -U solchef -d solchef -c "SELECT slug FROM prep_prepkit ORDER BY position, slug;"
```

Должно быть **135** и два slug наборов. Если 43 — залили не тот дамп или прогнали `import_v1`. Останавливайтесь.

Сборка и запуск (первый раз долго: Next `standalone` + gunicorn):

```bash
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
docker compose -f docker-compose.prod.yml --env-file .env ps
curl -fsS "http://127.0.0.1/healthz"
```

Снаружи: `http://<IP_ВМ>/`. Если фронт не собрался: `docker compose -f docker-compose.prod.yml --env-file .env logs frontend`.

Суперпользователь Django, если его не было в дампе:

```bash
docker compose -f docker-compose.prod.yml --env-file .env exec backend \
  uv run python manage.py createsuperuser
```

`/admin/` закрыт basic auth Caddy **и** логином Django.

### Смоук по IP (до DNS)

Откройте с телефона / другой сети, не только с ВМ:

| URL | Ожидание |
|-----|----------|
| `http://<IP>/` | витрина V2, не статический V1 |
| `http://<IP>/recipes` | книга, не пусто |
| `http://<IP>/recipes/<любой-slug>` | карточка |
| `http://<IP>/prep` | два сентябрьских набора |
| `http://<IP>/tips` | советы |
| `http://<IP>/calculator` | калькулятор |
| `http://<IP>/recipe.html?id=stejk-na-skovorode-pan-searing` | уводит на `/recipes/stejk-na-skovorode-pan-searing` |
| `http://<IP>/healthz` | живой backend |
| `http://<IP>/admin/` | сначала basic auth Caddy, потом форма Django |

Пока это не зелёное — DNS не трогать.

## 3. Домен: с GitHub Pages на ВМ

Сейчас у регистратора (как в архивном V1 PLAN):

- A: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
- при наличии www: CNAME `www` → `AterDeus.github.io` (или ваш github.io)

Сделайте так:

1. В панели хостера скопируйте **публичный IPv4** ВМ.
2. У регистратора **удалите** все A (и AAAA, если есть) GitHub Pages.
3. Добавьте **A** `sol-chef.ru` → IP ВМ.
4. `www`: либо A на тот же IP, либо CNAME на `sol-chef.ru`.
5. Если TTL был сутки — смена может идти часами. Перед окном лучше снизить TTL заранее.

Проверка, не с вашего кэша:

```bash
nslookup sol-chef.ru 8.8.8.8
```

Должен быть IP ВМ, не `185.199.*`.

Пока DNS не дошёл, Caddy **не** сможет выписать сертификат. Не переключайте `CADDYFILE` раньше времени. Сайт по IP в это время уже V2; по домену кто-то ещё может видеть Pages.

## 4. HTTPS

Когда `nslookup` уже показывает ВМ:

```bash
cd /opt/sol-chef/v2/infra
```

В `.env`:

```
CADDYFILE=./Caddyfile.prod
DJANGO_ALLOWED_HOSTS=sol-chef.ru,www.sol-chef.ru,backend,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://sol-chef.ru,https://www.sol-chef.ru
SITE_URL=https://sol-chef.ru
```

```bash
docker compose -f docker-compose.prod.yml --env-file .env up -d caddy backend frontend
docker compose -f docker-compose.prod.yml --env-file .env logs caddy
```

Откройте `https://sol-chef.ru`. Сертификат — Let's Encrypt через Caddy, отдельно ничего покупать не нужно. Повторите смоук с §2 по `https://sol-chef.ru`.

## 5. Выключить GitHub Pages

Только когда `https://sol-chef.ru` открывает **V2**.

1. GitHub → репозиторий → **Settings → Pages → Disable** (или Source: None).
2. Custom domain очистить, если поле ещё заполнено.
3. Файл `CNAME` в архиве (`archive/v1/CNAME`) больше не у корня — так и должно быть.
4. Теперь можно пушить локальный `main` (архив V1 + папка `v2/`).

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

Бэкап (DEFAULTS: сутки, 7 дней; медиа пока нет):

```bash
mkdir -p /opt/sol-chef/backups
docker compose -f docker-compose.prod.yml --env-file .env exec -T postgres \
  pg_dump -U solchef -d solchef --clean --if-exists --no-owner --no-acl | gzip > /opt/sol-chef/backups/solchef-$(date +%F).sql.gz
```

## Если что-то не так

| Симптом | Что проверить |
|---------|----------------|
| GitHub Pages после push отдаёт README | вы пушнули `main` до переключения DNS; верните Pages или ускорьте A-записи |
| Caddy: ACME error / NXDOMAIN | DNS ещё не на ВМ; держите `Caddyfile.http` |
| 502 на `/` | `docker compose … ps` — frontend/backend healthy? |
| `/admin/` 401 без формы Django | basic auth Caddy; хеш с удвоенными `$` в `.env` |
| Пустой каталог / 43 карточки | залили не тот дамп или прогнали `import_v1` на проде |
| CSRF на https | `DJANGO_CSRF_TRUSTED_ORIGINS` с `https://sol-chef.ru` |
| Сборка фронта убита / OOM | swap 4 ГБ; не собирать дважды параллельно |
| `psql` ругается на `restrict` | восстанавливайте **тем же** `postgres:16`, что в `docker-compose.prod.yml` |

Откат на V1 (только если DNS ещё можно вернуть на GitHub): снова A-записи `185.199.108–111.153`, включить Pages, branch `main` / root — и **не** пушить коммит без корневого `index.html`. После cutover откат = отдельное решение, архивный V1 сам по себе домен не обслуживает.
