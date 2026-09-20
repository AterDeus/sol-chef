# Спринт — cutover: V2 на ВМ и домен

Человек (чат 2026-09-18 / 2026-09-20): тестовый вариант сделать основным и зарелизить. ВМ `217.60.186.246`, Ubuntu 8 ГБ.

Не делать: пуш `main` до того, как `https://sol-chef.ru` отдаёт V2; `import_v1` на проде; Next/Django в корень; возврат V1 в корень; волны рецептов; оверлей осей; аккаунты.

## Цель

`sol-chef.ru` отдаёт 2.0: Caddy → Next + Django + Postgres. Каталог — дамп локальной БД (**255** карточек и два сентябрьских набора), не голый ETL V1.

Операции: [docs/CUTOVER.md](docs/CUTOVER.md).

## Чек-лист

- [x] V1 в `archive/v1/`, приложение только в `v2/` (локальный `main`; `origin/main` ещё старый корень).
- [x] Прод-compose, `Dockerfile.prod`, Caddy HTTP/HTTPS, `.env.example`.
- [x] Дамп локальной БД: `v2/infra/solchef.dump` (не в git).
- [x] Код на ВМ **без** push в `main` (scp/tar → `/opt/sol-chef`).
- [x] `.env` на ВМ: новые секреты, `CADDYFILE=./Caddyfile.http`, в `ALLOWED_HOSTS` IP ВМ.
- [x] Postgres+Redis → restore дампа → `count(*) = 255`, два slug наборов.
- [x] `docker compose -f docker-compose.prod.yml --env-file .env up -d --build` (починен `wsgi.py` + `DJANGO_SETTINGS_MODULE`).
- [x] Смоук по `http://217.60.186.246/`: витрина, `/recipes`, `/prep`, `/tips`, `/calculator`, редирект `recipe.html?id=`, `/healthz`.
- [ ] DNS A `sol-chef.ru` (и www) на `217.60.186.246`; `nslookup` через 8.8.8.8 не `185.199.*`.
- [ ] `Caddyfile.prod`, HTTPS, повтор смоука на `https://sol-chef.ru`.
- [ ] Выключить GitHub Pages.
- [ ] Пуш `main` только после зелёного HTTPS.

## Готово, когда

По `https://sol-chef.ru` открывается V2, каталог не 43 карточки, `/prep` показывает два набора, старый URL рецепта уводит на `/recipes/<slug>`.
