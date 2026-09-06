# frontend — Next.js 15

App Router, TypeScript. Прод-сборка: `output: 'standalone'`. Срез в Compose: `next dev`. UI по-русски, код по-английски.

Экраны: [../docs/UX-PROPOSAL.md](../docs/UX-PROPOSAL.md) (**D+**). Стек: [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md). Токены скопированы из корневого `css/global.css` (тот файл не перезаписывался).

`v2/preview/` не референс.

## Env

| Переменная | Кто | Compose |
|------------|-----|---------|
| `INTERNAL_API_URL` | сервер Next | `http://backend:8000` |
| `NEXT_PUBLIC_API_URL` | браузер | пустая строка → относительный `/api` |

SSR ходит на Django напрямую. Браузер — на `/api/` того же origin (Caddy). Не `localhost:8080` из контейнера frontend.

Публичных маршрутов в `app/api/` нет. `POST /_internal/revalidate` — rewrite на заглушку ISR (`/isr/revalidate`); снаружи Caddy отдаёт 404 на `/_internal/*`.

Масштаб рецепта считает Django. Клиент показывает `display_amount` из JSON.

## Скрипты

```bash
npm install
npm run dev    # :3000
npm run build
npm start
```
