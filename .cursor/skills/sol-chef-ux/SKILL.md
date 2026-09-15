---
name: sol-chef-ux
description: Analyzes and proposes sol-chef 2.0 information architecture and screens. Use when the user asks for UX review, IA, navigation, wireframes, or to prepare UX for another agent. Do not use v2/preview as a reference.
---

# UX sol-chef 2.0

Канон экранов уже принят: `v2/docs/UX-PROPOSAL.md` (**D+**, в UI «Калькулятор», `/calculator`). Этот скилл — только если просят переиграть IA. Реализация кода — `v2/CURRENT_SPRINT.md`, не этот скилл.

Переигровка: вход `v2/docs/UX.md`, правка proposal.

- Архив V1: `archive/v1/`, `python -m http.server 3456` из этой папки.
- `v2/preview/` не смотреть, не продолжать и не восстанавливать.
- Этот скилл не пишет код приложения. Next/Django — только в `v2/` по CURRENT_SPRINT. Не возвращать V1 в корень. Токены только из `archive/v1/css/global.css`.
- Принятое в `v2/docs/HUMAN.md` §3 (включая D+) не отменять без причины.
