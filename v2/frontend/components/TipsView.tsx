'use client';

import { useEffect, useId, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { EmptyState } from '@/components/Feedback';
import { HashDetailsOpener } from '@/components/HashDetailsOpener';
import {
  filterTips,
  flattenTips,
  groupedTips,
  isKnownKind,
  sectionCounts,
  tagsInSet,
  tipDomId,
  tipKindLabel,
  tipsListHref,
  type NormalizedTip,
  type TipsQuery,
} from '@/lib/tips';
import type { TipsPayload } from '@/lib/types';
import { TIP_KIND, TIP_TAG } from '@/lib/vocab';

function toggleCode(current: string, next: string): string {
  return current === next ? '' : next;
}

function syncTipsUrl(query: TipsQuery) {
  const next = `${tipsListHref(query)}${window.location.hash}`;
  const now = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  if (now !== next) {
    window.history.replaceState(null, '', next);
  }
}

function collapsedTipHeight(card: HTMLDetailsElement): number {
  const summary = card.querySelector('summary');
  if (!(summary instanceof HTMLElement)) return 0;
  const border = getComputedStyle(card);
  return (
    summary.getBoundingClientRect().height +
    (Number.parseFloat(border.borderTopWidth) || 0) +
    (Number.parseFloat(border.borderBottomWidth) || 0)
  );
}

function syncTipSlotHeight(slot: HTMLElement, card: HTMLDetailsElement) {
  const height = collapsedTipHeight(card);
  if (height > 0) slot.style.setProperty('--tip-slot-h', `${height}px`);
}

function tipMotionMs(el: Element): number {
  const raw = getComputedStyle(el).getPropertyValue('--duration').trim();
  const n = Number.parseFloat(raw);
  if (!Number.isFinite(n) || n <= 0) return 350;
  return raw.endsWith('ms') ? n : n * 1000;
}

function cssVarPx(el: HTMLElement, name: string, fallback: number): number {
  const raw = getComputedStyle(el).getPropertyValue(name).trim();
  const n = Number.parseFloat(raw);
  if (!Number.isFinite(n)) return fallback;
  if (raw.endsWith('rem')) {
    const root = Number.parseFloat(getComputedStyle(el.ownerDocument.documentElement).fontSize) || 16;
    return n * root;
  }
  return n;
}

function layoutTipsMasonry(container: HTMLElement) {
  const items = Array.from(container.children).filter((node): node is HTMLElement => node instanceof HTMLElement);
  const gap = cssVarPx(container, '--tips-gap', 10);
  const minCol = cssVarPx(container, '--tips-col-min', 264);
  const width = container.clientWidth;
  if (!items.length || width <= 0) {
    container.style.height = '';
    return;
  }

  const cols = Math.max(1, Math.floor((width + gap) / (minCol + gap)));
  const colWidth = (width - gap * (cols - 1)) / cols;
  const heights = Array.from({ length: cols }, () => 0);

  for (const item of items) {
    item.style.position = 'absolute';
    item.style.width = `${colWidth}px`;
    const card = item.querySelector(':scope > details.tip-card');
    if (card instanceof HTMLDetailsElement) syncTipSlotHeight(item, card);
  }

  for (const item of items) {
    const col = heights.indexOf(Math.min(...heights));
    const height = item.getBoundingClientRect().height;
    item.style.left = `${col * (colWidth + gap)}px`;
    item.style.top = `${heights[col]}px`;
    heights[col] += height + gap;
  }

  const tallest = Math.max(0, ...heights);
  const nextHeight = `${Math.max(0, tallest - gap)}px`;
  const signature = `${width}|${cols}|${nextHeight}|${items.map((item) => item.style.top + item.style.left).join('|')}`;
  if (container.dataset.masonrySig === signature) return;
  container.dataset.masonrySig = signature;
  container.style.height = nextHeight;
}

function TipsMasonry({ children, layoutKey }: { children: ReactNode; layoutKey: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const container = ref.current;
    if (!container) return undefined;

    const run = () => layoutTipsMasonry(container);
    run();
    container.classList.add('is-ready');

    const observer = new ResizeObserver(run);
    observer.observe(container);
    const seen = new Set<Element>();
    const watchKids = () => {
      for (const child of container.children) {
        if (child instanceof HTMLElement && !seen.has(child)) {
          seen.add(child);
          observer.observe(child);
        }
      }
    };
    watchKids();
    const mutations = new MutationObserver(() => {
      watchKids();
      run();
    });
    mutations.observe(container, { childList: true });

    return () => {
      observer.disconnect();
      mutations.disconnect();
    };
  }, [layoutKey]);

  return (
    <div className="tips-masonry" ref={ref}>
      {children}
    </div>
  );
}

function TipBadges({ tip }: { tip: NormalizedTip }) {
  const kindLabel = tipKindLabel(tip.kind);
  const tags = tip.tags
    .map((code) => ({ code, label: TIP_TAG[code] }))
    .filter((item) => item.label && item.label !== kindLabel);
  if (!kindLabel && tags.length === 0) return null;
  return (
    <p className="tip-card__badges">
      {kindLabel ? <span className="tip-badge tip-badge--kind">{kindLabel}</span> : null}
      {tags.map((item) => (
        <span key={item.code} className="tip-badge">
          {item.label}
        </span>
      ))}
    </p>
  );
}

function TipCard({
  tip,
  onOpen,
}: {
  tip: NormalizedTip;
  onOpen?: (el: HTMLDetailsElement) => void;
}) {
  if (!tip.explanation) {
    return (
      <article id={tipDomId(tip.id)} className="tip-slot tip-slot--static">
        <div className="tip-card tip-card--static">
          <div className="tip-card__face">
            <TipBadges tip={tip} />
            <p className="tip-card__hint">{tip.hint}</p>
          </div>
        </div>
      </article>
    );
  }

  return <ExpandableTipCard tip={tip} onOpen={onOpen} />;
}

function ExpandableTipCard({
  tip,
  onOpen,
}: {
  tip: NormalizedTip;
  onOpen?: (el: HTMLDetailsElement) => void;
}) {
  const slotRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLDetailsElement>(null);
  const raiseTimer = useRef(0);

  useEffect(() => () => window.clearTimeout(raiseTimer.current), []);

  useLayoutEffect(() => {
    const slot = slotRef.current;
    const card = cardRef.current;
    if (!slot || !card) return undefined;

    const sync = () => syncTipSlotHeight(slot, card);
    sync();

    const summary = card.querySelector('summary');
    const observer = new ResizeObserver(sync);
    observer.observe(slot);
    if (summary) observer.observe(summary);

    return () => observer.disconnect();
  }, [tip.hint, tip.kind, tip.tags.join(',')]);

  return (
    <div className="tip-slot" ref={slotRef}>
      <details
        ref={cardRef}
        id={tipDomId(tip.id)}
        className="tip-card"
        onToggle={(event) => {
          const card = event.currentTarget;
          const slot = slotRef.current;
          if (slot) syncTipSlotHeight(slot, card);
          window.clearTimeout(raiseTimer.current);
          if (card.open) {
            card.classList.add('tip-card--raised');
            onOpen?.(card);
            return;
          }
          const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          raiseTimer.current = window.setTimeout(
            () => {
              if (!card.open) card.classList.remove('tip-card--raised');
            },
            reduce ? 0 : tipMotionMs(card) + 20,
          );
        }}
      >
        <summary>
          <div className="tip-card__face">
            <TipBadges tip={tip} />
            <p className="tip-card__hint">{tip.hint}</p>
          </div>
        </summary>
        <div className="tip-card__reveal">
          <div className="tip-card__clip">
            <div className="tip-card__panel">
              <p className="tip-card__body">{tip.explanation}</p>
            </div>
          </div>
        </div>
      </details>
    </div>
  );
}

function ChipButton({
  label,
  pressed,
  count,
  showCount,
  onClick,
}: {
  label: string;
  pressed: boolean;
  count?: number;
  showCount?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      className={pressed ? 'chip is-active' : 'chip'}
      aria-pressed={pressed}
      onClick={onClick}
    >
      {label}
      {showCount ? <span className="chip__n">{count ?? 0}</span> : null}
    </button>
  );
}

export function TipsView({
  payload,
  omitLead = false,
  initialQ = '',
  initialKind = '',
  initialSection = '',
  initialTag = '',
}: {
  payload: TipsPayload;
  omitLead?: boolean;
  initialQ?: string;
  initialKind?: string;
  initialSection?: string;
  initialTag?: string;
}) {
  const searchId = useId();
  const [q, setQ] = useState(initialQ);
  const [qLive, setQLive] = useState(initialQ);
  const [kind, setKind] = useState(isKnownKind(initialKind) ? initialKind : '');
  const [section, setSection] = useState(initialSection);
  const [tag, setTag] = useState(initialTag);
  const sections = payload.sections ?? [];
  const all = useMemo(() => flattenTips(payload), [payload]);
  const query: TipsQuery = { q: qLive, kind, section, tag };
  const filtered = useMemo(() => filterTips(all, query), [all, qLive, kind, section, tag]);
  const groups = useMemo(() => groupedTips(sections, filtered), [sections, filtered]);
  const beforeTag = useMemo(
    () => filterTips(all, { q: qLive, kind, section, tag: '' }),
    [all, qLive, kind, section],
  );
  const tagCodes = useMemo(() => tagsInSet(beforeTag), [beforeTag]);
  const filtering = Boolean(qLive.trim() || kind || tag);
  const counts = useMemo(
    () => sectionCounts(all, query, sections.map((item) => item.id)),
    [all, qLive, kind, tag, section, sections],
  );
  const watch = filtered.map((item) => item.id).join(',');
  const resultsRef = useRef<HTMLDivElement>(null);
  const gridBooted = useRef(false);

  const closeOtherTips = (opened: HTMLDetailsElement) => {
    opened
      .closest('.tips-handbook')
      ?.querySelectorAll('details.tip-card')
      .forEach((node) => {
        if (node instanceof HTMLDetailsElement && node !== opened) node.open = false;
      });
  };

  useLayoutEffect(() => {
    const root = resultsRef.current;
    if (!root) return;
    const layoutAll = () => {
      root.querySelectorAll('.tips-masonry').forEach((node) => {
        if (!(node instanceof HTMLElement)) return;
        layoutTipsMasonry(node);
        node.classList.add('is-ready');
      });
    };
    layoutAll();
    root.classList.add('is-ready');
    root.setAttribute('aria-busy', 'false');
    layoutAll();
    if (gridBooted.current) return;
    gridBooted.current = true;
    const id = decodeURIComponent(window.location.hash.replace(/^#/, ''));
    if (!id) return;
    document.getElementById(id)?.scrollIntoView({ block: 'start' });
  }, [watch]);

  useEffect(() => {
    syncTipsUrl({ q: qLive, kind, section, tag });
  }, [qLive, kind, section, tag]);

  useEffect(() => {
    if (q === qLive) return undefined;
    const timer = window.setTimeout(() => {
      setQLive(q);
    }, 140);
    return () => window.clearTimeout(timer);
  }, [q, qLive]);

  if (all.length === 0) {
    return (
      <>
        {!omitLead && payload.intro ? <p className="lede">{payload.intro}</p> : null}
        <EmptyState>Пока нет советов.</EmptyState>
      </>
    );
  }

  return (
    <div className="tips-handbook">
      <HashDetailsOpener watch={watch} exclusive=".tips-handbook details.tip-card" />
      {!omitLead && payload.intro ? <p className="lede">{payload.intro}</p> : null}

      <form
        className="tips-search"
        action="/tips"
        method="get"
        onSubmit={(event) => {
          event.preventDefault();
          syncTipsUrl(query);
        }}
      >
        <label className="tips-search__label" htmlFor={searchId}>
          Что хотите узнать?
        </label>
        <div className="search-row">
          <input
            id={searchId}
            type="search"
            name="q"
            value={q}
            placeholder="Например: бисквит, мука, заморозка, духовка"
            autoComplete="off"
            onChange={(event) => setQ(event.target.value)}
          />
        </div>
        {kind ? <input type="hidden" name="kind" value={kind} /> : null}
        {section ? <input type="hidden" name="section" value={section} /> : null}
        {tag ? <input type="hidden" name="tag" value={tag} /> : null}
      </form>

      <fieldset className="filter-block">
        <legend className="filter-legend">Разделы</legend>
        <div className="chip-row tips-chips">
          {sections.map((item) => (
            <ChipButton
              key={item.id}
              label={item.title}
              pressed={section === item.id}
              count={counts.get(item.id) || 0}
              showCount={filtering}
              onClick={() => setSection((prev) => toggleCode(prev, item.id))}
            />
          ))}
        </div>
      </fieldset>

      <fieldset className="filter-block">
        <legend className="filter-legend">Тип</legend>
        <div className="chip-row tips-chips">
          {Object.entries(TIP_KIND).map(([code, label]) => (
            <ChipButton
              key={code}
              label={label}
              pressed={kind === code}
              onClick={() => setKind((prev) => toggleCode(prev, code))}
            />
          ))}
        </div>
      </fieldset>

      {tagCodes.length > 0 ? (
        <fieldset className="filter-block">
          <legend className="filter-legend">Тема</legend>
          <div className="chip-row tips-chips">
            {tagCodes.map((code) => (
              <ChipButton
                key={code}
                label={TIP_TAG[code]}
                pressed={tag === code}
                onClick={() => setTag((prev) => toggleCode(prev, code))}
              />
            ))}
          </div>
        </fieldset>
      ) : null}

      {filtered.length === 0 ? (
        <EmptyState>Ничего не найдено</EmptyState>
      ) : (
        <div className="tips-results" ref={resultsRef} aria-busy="true">
          <div className="tips-loader" role="status">
            <span className="tips-loader__spin" aria-hidden="true" />
            Загружаем советы
          </div>
          {groups.map((group) => (
            <section
              key={group.id}
              id={`tip-${group.id}`}
              className="tips-section"
              aria-labelledby={`tips-h-${group.id}`}
            >
              <h2 id={`tips-h-${group.id}`}>
                {group.title}
                {filtering ? <span className="tips-section__n">{group.items.length}</span> : null}
              </h2>
              <TipsMasonry layoutKey={group.items.map((item) => item.id).join(',')}>
                {group.items.map((item) => (
                  <TipCard key={item.id} tip={item} onOpen={closeOtherTips} />
                ))}
              </TipsMasonry>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
