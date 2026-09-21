# frontend — Next.js 15

App Router, TypeScript. Прод-сборка: `output: 'standalone'`. Срез в Compose: `next dev`. UI по-русски, код по-английски.

Экраны: [../docs/UX-PROPOSAL.md](../docs/UX-PROPOSAL.md) (**D+**). Стек: [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md). Токены скопированы из `archive/v1/css/global.css` (тот файл не перезаписывался).

`v2/preview/` не референс.

## Env

| Переменная | Кто | Compose |
|------------|-----|---------|
| `INTERNAL_API_URL` | сервер Next | `http://backend:8000` |
| `NEXT_PUBLIC_API_URL` | браузер | пустая строка → относительный `/api` |
| `SITE_URL` | сервер Next | публичный origin sitemap / canonical. Локально `http://localhost:8080` |

SSR ходит на Django напрямую. Браузер — на `/api/` того же origin (Caddy). Не `localhost:8080` из контейнера frontend.

Публичных маршрутов в `app/api/` нет. `POST /_internal/revalidate` — rewrite на заглушку ISR (`/isr/revalidate`); снаружи Caddy отдаёт 404 на `/_internal/*`.

Масштаб рецепта считает Django. Клиент показывает `display_amount` из JSON.

## Скрипты

При работающем локальном Compose frontend уже запущен в Docker как `next dev`. Не выполняйте на хосте `npm run build`: папка `.next` смонтирована в контейнер, и production-сборка ломает ссылки dev-сервера на чанки. Для проверки типов используйте `npx tsc --noEmit`; production-сборка выполняется в образе из `Dockerfile.prod`.

```bash
npm install
npm run dev    # :3000
npm run build  # только вне запущенного local Compose
npm start
```
