import Link from 'next/link';

export default function NotFound() {
  return (
    <>
      <h1>Страница не найдена</h1>
      <p className="lede">Такого адреса нет. Вернитесь на витрину или в книгу рецептов.</p>
      <p>
        <Link href="/">На главную</Link>
        {' · '}
        <Link href="/recipes">Все рецепты</Link>
      </p>
    </>
  );
}
