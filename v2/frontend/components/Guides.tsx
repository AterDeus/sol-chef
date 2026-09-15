import type { GrainsPayload, MeatPayload } from '@/lib/types';
import { EmptyState } from '@/components/Feedback';

export function GrainsView({
  payload,
  omitLead = false,
}: {
  payload: GrainsPayload;
  omitLead?: boolean;
}) {
  const rows = payload.rows ?? [];
  return (
    <>
      {!omitLead && (payload.intro_lead || payload.intro) && (
        <p className="lede">
          {payload.intro_lead ? <strong>{payload.intro_lead} </strong> : null}
          {payload.intro}
        </p>
      )}
      {rows.length === 0 ? (
        <EmptyState>Пока нет таблицы круп.</EmptyState>
      ) : (
        <>
          <table className="grains">
            <caption className="sr-only">Крупы: промывка, вода, время</caption>
            <thead>
              <tr>
                <th scope="col">Крупа</th>
                <th scope="col">Промывка</th>
                <th scope="col">Вода</th>
                <th scope="col">Время</th>
                <th scope="col">Нюанс</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.name}>
                  <td className="name">{row.name}</td>
                  <td>{row.wash}</td>
                  <td className="ratio">{row.ratio}</td>
                  <td>{row.time}</td>
                  <td className="note">{row.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="grain-cards">
            {rows.map((row) => (
              <article key={row.name} className="grain-card">
                <h3>{row.name}</h3>
                <p>
                  <span className="ratio">{row.ratio}</span> · {row.time}
                </p>
                <p className="note">Промывка: {row.wash}</p>
                <p className="note">{row.note}</p>
              </article>
            ))}
          </div>
        </>
      )}
    </>
  );
}

export function MeatView({
  payload,
  omitLead = false,
}: {
  payload: MeatPayload;
  omitLead?: boolean;
}) {
  const methods = payload.methods ?? [];
  return (
    <>
      {!omitLead && (payload.intro_lead || payload.intro) && (
        <p className="lede">
          {payload.intro_lead ? <strong>{payload.intro_lead} </strong> : null}
          {payload.intro}
        </p>
      )}
      {methods.length === 0 ? (
        <EmptyState>Пока нет карточек по этому мясу.</EmptyState>
      ) : (
        methods.map((method) => (
          <section key={method.name} className="method-block">
            <div className="method-head">
              <h2>{method.name}</h2>
              <span className="sub">{method.sub}</span>
            </div>
            <div className="cards">
              {method.cards.map((card) => (
                <article key={card.title} className="card">
                  <h3>{card.title}</h3>
                  <div className="readout">
                    <span className="lbl">{card.readout_label}</span>
                    {card.readout_value}
                  </div>
                  <p>{card.text}</p>
                  <p className="pitfall">
                    <b>Ошибка:</b> {card.pitfall}
                  </p>
                </article>
              ))}
            </div>
          </section>
        ))
      )}
    </>
  );
}
