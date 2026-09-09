type Props = {
  name: string;
  className?: string;
  size?: number;
};

export function SpriteIcon({ name, className = 'ui-icon', size = 22 }: Props) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      aria-hidden
      focusable="false"
    >
      <use href={`/icons.svg?v=11#icon-${name}`} />
    </svg>
  );
}
