import type { GrainsPayload, MeatPayload, TipsPayload } from '@/lib/types';
import { EmptyState } from '@/components/Feedback';
import { HashDetailsOpener } from '@/components/HashDetailsOpener';

export function GrainsView({ payload }: { payload: GrainsPayload }) {
  const rows = payload.rows ?? [];
  return (
    <>
      {(payload.intro_lead || payload.intro) && (
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

export function MeatView({ payload }: { payload: MeatPayload }) {
  const methods = payload.methods ?? [];
  return (
    <>
      {(payload.intro_lead || payload.intro) && (
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

export function TipsView({ payload }: { payload: TipsPayload }) {
  const sections = payload.sections ?? [];
  return (
    <>
      <HashDetailsOpener />
      {payload.intro && <p className="lede">{payload.intro}</p>}
      {sections.length === 0 ? (
        <EmptyState>Пока нет советов.</EmptyState>
      ) : (
        sections.map((section) => (
          <details key={section.id} id={`tip-${section.id}`} className="tips-acc">
            <summary>{section.title}</summary>
            <ul>
              {section.items.map((item, index) => {
                if (typeof item === 'string') {
                  return <li key={index}>{item}</li>;
                }
                return (
                  <li key={index}>
                    {item.hint}
                    {item.explanation ? <span className="expl">{item.explanation}</span> : null}
                  </li>
                );
              })}
            </ul>
          </details>
        ))
      )}
    </>
  );
}
