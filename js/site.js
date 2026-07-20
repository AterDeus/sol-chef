import { fetchJson, setMeta, setOg } from './utils.js';

export function loadSite() {
  fetchJson('data/site.json')
    .then(site => {
      const eyebrow = document.getElementById('site-eyebrow');
      const heading = document.getElementById('site-heading');
      const tagline = document.getElementById('site-tagline');
      if (eyebrow && site.eyebrow) eyebrow.textContent = site.eyebrow;
      if (heading && site.heading) heading.textContent = site.heading;
      if (tagline && site.tagline) tagline.textContent = site.tagline;
      if (site.title) document.title = site.title;
      if (site.description) setMeta('description', site.description);
      if (site.theme_color) setMeta('theme-color', site.theme_color);
      if (site.title) setOg('og:title', site.title);
      if (site.description) setOg('og:description', site.description);
      if (site.domain) setOg('og:url', `https://${site.domain}/`);
    })
    .catch(() => { /* defaults in HTML */ });
}
