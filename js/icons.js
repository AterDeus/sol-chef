const ICON_SPRITE = 'assets/images/icons.svg';

export function spriteIconHtml(name, className = 'ui-icon') {
  return `<svg class="${className}" aria-hidden="true"><use href="${ICON_SPRITE}#icon-${name}"></use></svg>`;
}
