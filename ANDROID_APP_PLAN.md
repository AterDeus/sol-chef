# sol-chef — план Android-приложения (Capacitor + RuStore)

Личная кулинарная шпаргалка как Android-приложение.  
Сайт: [PLAN.md](PLAN.md) · RuStore: бесплатная публикация для физлица (без монетизации).

---

## Текущее состояние UX (реализовано)

- **Режим готовки** на `recipe.html` — пошаговый экран, таймеры, Wake Lock
- **prep** — напоминания заранее (разморозка, маринад, комнат. темп.) с push-уведомлениями
- **steps** — строка или объект с `timer_min` / `timer_sec`

---

## Главное: как будут обновляться рецепты

**Да — ваш текущий workflow сохраняется.** Вы по-прежнему добавляете записи в `data/recipes.json` (и другие JSON), делаете `git push`, GitHub Pages обновляет сайт — и **новые рецепты появляются в приложении без перевыпуска APK**.

### Схема

```
Вы правите JSON в Cursor
        ↓
git push → GitHub Pages (sol-chef.ru)
        ↓
Приложение при запуске (с интернетом) запрашивает:
  https://sol-chef.ru/data/recipes.json
  https://sol-chef.ru/data/tips.json
  … и остальные data/*.json
        ↓
Новый рецепт виден в приложении (обычно через 1–2 мин после деплоя)
```

### Что лежит где

| Часть | Где живёт | Как обновляется |
|-------|-----------|-----------------|
| Рецепты, советы, справочники | `data/*.json` на GitHub Pages | **Push в git** — без новой версии приложения |
| HTML, CSS, JS (оболочка) | В APK (папка `www/`) | Новая версия в RuStore (редко, при изменении UI/логики) |
| Кэш для offline | На телефоне (Service Worker) | Обновляется автоматически при успешной загрузке с сайта |

### Offline

- **С интернетом:** всегда свежие данные с `sol-chef.ru`.
- **Без интернета:** последняя успешно загруженная версия JSON (кэш).
- Если пользователь ни разу не открывал приложение онлайн — показывается встроенная копия JSON из APK (fallback при первой установке).

### Когда нужна новая версия в RuStore

Только если меняете **код приложения**, а не контент:

- новый экран, кнопка, таймер;
- правки в `js/`, `css/`, `index.html`;
- новые нативные плагины Capacitor.

Добавление 10 рецептов в JSON → **только push на GitHub**, RuStore трогать не нужно.

---

## Архитектура

```
┌─────────────────────────────────────────┐
│  Android APK (Capacitor)                │
│  ┌───────────────────────────────────┐  │
│  │ www/ — HTML, CSS, JS, fallback JSON│  │
│  └───────────────────────────────────┘  │
│           │ fetch (online)              │
│           ▼                             │
│  https://sol-chef.ru/data/*.json       │
│  (источник правды = GitHub Pages)       │
└─────────────────────────────────────────┘
```

**Почему Capacitor, а не «просто WebView на сайт»:**

- RuStore требует **самостоятельный продукт** — offline-кэш, иконка, splash, работа без сети частично.
- Можно добавить нативные фичи позже: Share, «экран не гаснет», таймеры, haptic.
- Один репозиторий: сайт и приложение из одних файлов.

**Package name (пример):** `ru.solchef.app` — задаётся один раз, потом не меняется.

---

## Что понадобится

### Аккаунты и доступ

| Что | Зачем | Стоимость |
|-----|-------|-----------|
| [RuStore Консоль](https://www.rustore.ru/developer) | Публикация APK/AAB | Бесплатно |
| VK ID | Вход в RuStore Консоль | Бесплатно |
| GitHub + домен `sol-chef.ru` | Хостинг JSON и сайта | Домен ~500–1500 ₽/год |
| Google Android Developer (с 2027) | Верификация package name для установки на сертифицированных Android | См. [требования Google](https://www.rustore.ru/help/developers/publishing-and-verifying-apps/app-publication/package-name-verification) |

Для **бесплатного** приложения без монетизации достаточно аккаунта **физлица** в RuStore.

### ПО на компьютере (Windows)

1. **Node.js** LTS (20+) — [nodejs.org](https://nodejs.org/)
2. **Android Studio** — [developer.android.com/studio](https://developer.android.com/studio)
   - При установке: Android SDK, Android SDK Platform, Android Virtual Device
3. **JDK 17** — обычно идёт с Android Studio
4. **Git** — уже есть

### Переменные окружения (Windows)

После установки Android Studio добавьте (PowerShell, профиль пользователя):

```powershell
[System.Environment]::SetEnvironmentVariable("ANDROID_HOME", "$env:LOCALAPPDATA\Android\Sdk", "User")
```

В PATH (через «Переменные среды» Windows):

```
%LOCALAPPDATA%\Android\Sdk\platform-tools
%LOCALAPPDATA%\Android\Sdk\tools
```

Проверка:

```powershell
node -v
npm -v
adb version
```

---

## Этапы разработки

Статус: `[ ]` не начат · `[~]` в работе · `[x]` готов

---

### Этап 0: Предусловия

**Цель:** сайт на HTTPS, домен готов к загрузке JSON из приложения.

- [ ] Репозиторий на GitHub, включён GitHub Pages
- [ ] Домен `sol-chef.ru` → GitHub Pages (или временно `username.github.io/sol-chef/` для тестов)
- [ ] `https://sol-chef.ru/data/recipes.json` открывается в браузере
- [ ] CORS: для `fetch` с того же origin проблем нет; JSON отдаётся с того же домена — доп. настройки не нужны

**Оценка:** 0–2 ч (если домен уже есть — 0)

---

### Этап 1: Remote data layer

**Цель:** JS умеет грузить JSON с production-URL, с fallback на локальные файлы.

- [ ] Создать `js/config.js`:
  - `DATA_BASE_URL` — `https://sol-chef.ru/data/` (или относительный `./data/` для локальной разработки)
  - определение: Capacitor / localhost / github.io
- [ ] Обновить `fetchJson` в `js/utils.js` — stale-while-revalidate:
  1. показать кэш (если есть),
  2. запросить с `DATA_BASE_URL`,
  3. обновить UI и кэш
- [ ] Подключить `config.js` во все модули: `recipes.js`, `tips.js`, `reference.js`, `site.js`, `recipe-page.js`
- [ ] Проверить локально и на GitHub Pages

**Файлы:** `js/config.js`, `js/utils.js`, модули в `js/`  
**Оценка:** 2–3 ч

**Промпт для Cursor:**

```
Реализуй Этап 1 из ANDROID_APP_PLAN.md: remote data layer.
DATA_BASE_URL = https://sol-chef.ru/data/ в production.
Offline: cache в localStorage или IndexedDB, fallback на ./data/.
```

---

### Этап 2: PWA и offline

**Цель:** приложение и сайт кэшируют статику и JSON.

- [ ] `manifest.webmanifest` — имя, иконки 192/512, `display: standalone`, `theme_color: #1B1713`
- [ ] Иконки приложения: `assets/icon-192.png`, `assets/icon-512.png` (из favicon или новый дизайн)
- [ ] `sw.js` — Service Worker:
  - cache-first для CSS/JS/HTML
  - network-first или stale-while-revalidate для `data/*.json`
- [ ] Регистрация SW в `js/main.js` и `js/recipe-page.js`
- [ ] `<link rel="manifest">` в `index.html`, `recipe.html`

**Файлы:** `manifest.webmanifest`, `sw.js`, `index.html`, `recipe.html`, `assets/`  
**Оценка:** 3–4 ч

---

### Этап 3: Capacitor — инициализация

**Цель:** Android-проект в репозитории, сборка debug APK.

- [ ] В корне репозитория:

```bash
npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init "sol-chef" ru.solchef.app --web-dir www
```

- [ ] Скрипт копирования сайта в `www/` (без `node_modules`, `.git`, `android/`):

```json
"scripts": {
  "build:web": "node scripts/copy-www.js",
  "cap:sync": "npm run build:web && npx cap sync android",
  "cap:open": "npx cap open android"
}
```

- [ ] `scripts/copy-www.js` — копирует: `index.html`, `recipe.html`, `style.css`, `css/`, `js/`, `data/`, `assets/`, `manifest.webmanifest`, `sw.js`
- [ ] `npx cap add android`
- [ ] `capacitor.config.ts` / `.json`:

```json
{
  "appId": "ru.solchef.app",
  "appName": "sol-chef",
  "webDir": "www",
  "server": {
    "androidScheme": "https"
  },
  "android": {
    "allowMixedContent": false
  }
}
```

- [ ] **Не** использовать `server.url` на постоянной основе — иначе offline ломается; remote только для JSON через `config.js`

- [ ] `.gitignore` дополнить:

```
node_modules/
www/
android/app/build/
android/.gradle/
*.apk
*.aab
local.properties
```

- [ ] `npm run cap:sync` → `npx cap open android` → Run на эмуляторе или телефоне

**Файлы:** `package.json`, `capacitor.config.json`, `scripts/copy-www.js`, `android/`, `.gitignore`  
**Оценка:** 3–4 ч

---

### Этап 4: Нативная полировка Android

**Цель:** приложение выглядит «как своё», а не как сайт в браузере.

- [ ] `@capacitor/splash-screen` — splash `#1B1713`, логотип
- [ ] `@capacitor/status-bar` — тёмный status bar под тему
- [ ] Adaptive icon (foreground + background) в `android/app/src/main/res/`
- [ ] `@capacitor/app` — кнопка «Назад»: на главной — выход, на рецепте — назад к списку
- [ ] `@capacitor/share` — «Поделиться рецептом» (опционально)
- [ ] `@capacitor/keep-awake` — «Режим готовки» на странице рецепта (опционально)
- [ ] `AndroidManifest.xml`: `INTERNET`, `ACCESS_NETWORK_STATE`
- [ ] Проверка safe-area, `bottom-nav` не перекрывается системной навигацией

**Оценка:** 4–6 ч

---

### Этап 5: Подпись и release-сборка

**Цель:** подписанный AAB для RuStore.

#### 5.1 Keystore (один раз, хранить навсегда)

```bash
keytool -genkey -v -keystore sol-chef-release.keystore -alias sol-chef -keyalg RSA -keysize 2048 -validity 10000
```

- Файл `sol-chef-release.keystore` — **не коммитить**, бэкап в надёжное место
- Пароли — в менеджер паролей

#### 5.2 Настройка signing в Android Studio

`android/app/build.gradle` — `signingConfigs` + `buildTypes.release`

Или через Android Studio: **Build → Generate Signed Bundle / APK → Android App Bundle**

#### 5.3 Версионирование

В `android/app/build.gradle`:

```gradle
versionCode 1      // +1 при каждой загрузке в RuStore
versionName "1.0.0"
```

- **Контент (JSON):** версию APK не трогаете  
- **Код приложения:** `versionCode++`, обновить `versionName`

**Оценка:** 2–3 ч (первый раз)

---

### Этап 6: Публикация в RuStore

**Цель:** приложение в магазине, модерация пройдена.

#### 6.1 Регистрация

1. [console.rustore.ru](https://console.rustore.ru/) → вход через VK ID
2. Тип аккаунта: **физлицо** (если без монетизации)
3. Заполнить профиль разработчика

#### 6.2 Карточка приложения

| Поле | Рекомендация |
|------|--------------|
| Название | sol-chef — кухонная шпаргалка |
| Краткое описание | Крупы, мясо, советы шефов и рецепты — офлайн-справочник |
| Категория | Еда и напитки / Справочники |
| Возрастной рейтинг | 0+ |
| Package name | `ru.solchef.app` (как в Capacitor) |
| Политика конфиденциальности | URL на GitHub Pages, напр. `https://sol-chef.ru/privacy.html` |

#### 6.3 Материалы

- **Иконка:** 512×512 PNG
- **Скриншоты:** минимум 2, лучше 4–6 (телефон, тёмная тема, рецепт, справочник)
- **APK или AAB:** release, подписанный
- Для **AAB:** подписи загружаются отдельно в RuStore (см. [инструкцию RuStore](https://www.rustore.ru/help/developers/publishing-and-verifying-apps/app-publication))

#### 6.4 Модерация

- Обычно ~1 час, иногда до 1–3 дней
- RuStore проверяет: работоспособность, не «пустая оболочка сайта», актуальные скриншоты
- Offline + кэш + иконка/splash повышают шансы одобрения

#### 6.5 Google package verification (2026–2027)

Зарегистрируйте package name в [Google Play Console](https://play.google.com/console/) до глобального требования (2027), даже если в Google Play не публикуете.  
Инструкция RuStore: [package-name-verification](https://www.rustore.ru/help/developers/publishing-and-verifying-apps/app-publication/package-name-verification)

**Оценка:** 2–4 ч (+ ожидание модерации)

---

### Этап 7: Политика конфиденциальности

**Цель:** обязательная страница для RuStore.

- [ ] `privacy.html` — простая статическая страница:
  - какие данные собираются (минимум: ничего / только локальный кэш)
  - обращение к `sol-chef.ru` за JSON
  - контакты разработчика
- [ ] Ссылка в RuStore и в настройках приложения (опционально)

**Оценка:** 1 ч

---

## Пошаговая инструкция (первый запуск Capacitor)

Выполняйте по порядку после **Этапов 1–2** (remote JSON + PWA).

### Шаг 1. Node и зависимости

```powershell
cd K:\Work\sol-chef
npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/android
npm install -D typescript  # опционально
```

### Шаг 2. Инициализация Capacitor

```powershell
npx cap init "sol-chef" ru.solchef.app --web-dir www
```

### Шаг 3. Скрипт сборки www

Создайте `scripts/copy-www.js` (см. Этап 3) и добавьте `"build:web"` в `package.json`.

### Шаг 4. Первый sync

```powershell
npm run build:web
npx cap add android
npx cap sync android
```

### Шаг 5. Android Studio

```powershell
npx cap open android
```

- Дождитесь Gradle sync
- Подключите телефон (USB debugging) или запустите эмулятор
- **Run** (зелёный треугольник)

### Шаг 6. Проверка обновления контента

1. Добавьте тестовый рецепт в `data/recipes.json`
2. `git push` → дождитесь GitHub Pages
3. На телефоне: закройте приложение, откройте снова (с Wi‑Fi)
4. Новый рецепт должен появиться **без** пересборки APK

### Шаг 7. Release для RuStore

1. Создайте keystore (Этап 5)
2. **Build → Generate Signed Bundle / APK**
3. Загрузите `.aab` в RuStore Консоль
4. Заполните карточку, отправьте на модерацию

---

## Ежедневный workflow после запуска

### Добавить рецепт (как сейчас)

```
1. Cursor → правка data/recipes.json (через ИИ или вручную)
2. node scripts/validate-recipes.js
3. git add data/recipes.json && git commit && git push
4. Через 1–2 мин — на сайте и в приложении (при следующем открытии online)
```

### Изменить дизайн или логику приложения

```
1. Правки в html/css/js
2. npm run cap:sync
3. Сборка signed AAB, versionCode +1
4. Загрузка новой версии в RuStore
```

### Локальная разработка приложения

```powershell
# Терминал 1 — сайт
python -m http.server 3456

# Терминал 2 — после правок
npm run cap:sync
npx cap open android
```

Для теста remote JSON локально временно в `js/config.js` укажите production URL или локальный `./data/`.

---

## Структура репозитория (целевая)

```
sol-chef/
├── index.html
├── recipe.html
├── manifest.webmanifest      # этап 2
├── sw.js                     # этап 2
├── privacy.html              # этап 7
├── package.json              # этап 3
├── capacitor.config.json     # этап 3
├── scripts/
│   ├── copy-www.js           # этап 3
│   └── validate-*.js
├── js/
│   ├── config.js             # этап 1 — DATA_BASE_URL
│   └── ...
├── data/                     # источник правды (git)
├── android/                  # генерируется Capacitor (коммитить можно)
├── www/                      # генерируется copy-www (в .gitignore)
├── ANDROID_APP_PLAN.md       # этот файл
└── PLAN.md
```

---

## Риски и решения

| Риск | Решение |
|------|---------|
| RuStore отклонит «просто сайт» | Offline-кэш, splash, иконка, Share, режим готовки |
| Нет интернета на кухне | Service Worker + fallback JSON в APK |
| Забыли keystore | Бэкап keystore; без него нельзя обновлять приложение в store |
| GitHub Pages недоступен | Показываем последний кэш; badge «данные от …» |
| Шрифты Google Fonts offline | Позже: self-host шрифтов в `assets/fonts/` |
| Требование Google 2027 | Зарегистрировать package name заранее |

---

## Оценка времени

| Этап | Часы |
|------|------|
| 0. Предусловия (домен) | 0–2 |
| 1. Remote data layer | 2–3 |
| 2. PWA + offline | 3–4 |
| 3. Capacitor init | 3–4 |
| 4. Нативная полировка | 4–6 |
| 5. Подпись release | 2–3 |
| 6. RuStore | 2–4 |
| 7. Privacy policy | 1 |
| **Итого** | **~17–27 ч** |

---

## Рекомендуемый порядок

**Неделя 1:** Этапы 0 → 1 → 2 (сайт готовит JSON для приложения)  
**Неделя 2:** Этапы 3 → 4 (первый APK на телефоне)  
**Неделя 3:** Этапы 5 → 6 → 7 (RuStore)

После Этапа 3 уже можно пользоваться приложением sideload (APK вручную), RuStore — когда готовы материалы и privacy.

---

## Промпты для Cursor

```
Реализуй Этап 1 из ANDROID_APP_PLAN.md: js/config.js и remote fetch для data/*.json.
```

```
Реализуй Этап 2 из ANDROID_APP_PLAN.md: manifest.webmanifest, sw.js, иконки.
```

```
Реализуй Этап 3 из ANDROID_APP_PLAN.md: package.json, copy-www.js, Capacitor android.
```

---

## Журнал прогресса

| Дата | Этап | Что сделано |
|------|------|-------------|
| 2026-07-21 | — | Создан ANDROID_APP_PLAN.md |

*Заполняйте по мере выполнения.*

---

## Полезные ссылки

- [Capacitor — Getting Started](https://capacitorjs.com/docs/getting-started)
- [Capacitor Android](https://capacitorjs.com/docs/android)
- [RuStore — публикация приложения](https://www.rustore.ru/help/developers/publishing-and-verifying-apps/app-publication)
- [RuStore — требования к приложениям](https://www.rustore.ru/help/developers/publishing-and-verifying-apps/requirement-apps)
- [RuStore — верификация package name](https://www.rustore.ru/help/developers/publishing-and-verifying-apps/app-publication/package-name-verification)
