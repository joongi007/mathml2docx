/* Navigation, locale-local search and code copying; page content needs no JavaScript. */
(() => {
  'use strict';
  document.documentElement.classList.remove('no-js');
  const body = document.body;
  const menu = document.querySelector('.menu-toggle');
  const sidebar = document.getElementById('navigation');
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    sidebar.classList.toggle('is-open', open);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      if (document.getElementById('docs-search').value) { clearSearch(); }
      else { sidebar.classList.remove('is-open'); menu.setAttribute('aria-expanded', 'false'); }
    }
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault(); sidebar.classList.add('is-open'); menu.setAttribute('aria-expanded', 'true');
      document.getElementById('docs-search').focus();
    }
  });
  for (const wrapper of document.querySelectorAll('.codehilite')) {
    const code = wrapper.querySelector('code, pre');
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'copy-code'; button.textContent = body.dataset.copy;
    button.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(code.textContent); button.textContent = body.dataset.copied; }
      catch (_) { button.textContent = body.dataset.copyFailed; }
      setTimeout(() => { button.textContent = body.dataset.copy; }, 2200);
    });
    wrapper.append(button);
  }
  const input = document.getElementById('docs-search');
  const clear = document.getElementById('clear-search');
  const panel = document.getElementById('search-panel');
  const status = document.getElementById('search-status');
  const results = document.getElementById('search-results');
  let index = null; let generation = 0; let timer;
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase();
  function clearSearch() { input.value = ''; panel.hidden = true; clear.hidden = true; results.replaceChildren(); generation++; input.focus(); }
  clear.addEventListener('click', clearSearch);
  input.addEventListener('input', () => {
    clearTimeout(timer);
    const current = ++generation;
    const query = input.value.trim();
    clear.hidden = !query; panel.hidden = !query;
    if (!query) { results.replaceChildren(); return; }
    timer = setTimeout(() => search(query, current), 140);
  });
  async function search(query, current) {
    status.textContent = body.dataset.searching;
    try {
      if (!index) {
        const response = await fetch(body.dataset.searchIndex);
        if (!response.ok) { throw new Error('Search unavailable'); }
        const data = await response.json();
        index = data.docs;
      }
      if (current !== generation) { return; }
      const terms = normalize(query).split(/\s+/);
      const matches = index.map(doc => {
        const title = normalize(doc.title + ' ' + doc.heading); const text = normalize(doc.text);
        const score = terms.reduce((total, term) => total + (title.includes(term) ? 5 : text.includes(term) ? 1 : -1000), 0);
        return {doc, score};
      }).filter(item => item.score > 0).sort((a, b) => b.score - a.score).slice(0, 12);
      results.replaceChildren();
      status.textContent = matches.length ? matches.length + ' ' + body.dataset.count : body.dataset.empty;
      for (const {doc} of matches) {
        const base = new URL(body.dataset.localeBase, location.href);
        const destination = new URL(doc.location, base);
        if (destination.origin !== location.origin || !destination.pathname.startsWith(base.pathname)) { continue; }
        const item = document.createElement('li'); const link = document.createElement('a');
        link.href = destination.href;
        const title = document.createElement('strong'); title.textContent = doc.heading === doc.title ? doc.title : doc.title + ' › ' + doc.heading;
        const snippet = document.createElement('small');
        const at = normalize(doc.text).indexOf(terms[0]); const start = Math.max(0, at - 30);
        snippet.textContent = (start ? '…' : '') + doc.text.slice(start, start + 130);
        link.append(title, snippet); item.append(link); results.append(item);
      }
    } catch (_) { if (current === generation) { results.replaceChildren(); status.textContent = body.dataset.failed; index = null; } }
  }
  input.addEventListener('keydown', event => {
    const first = results.querySelector('a');
    if (first && (event.key === 'ArrowDown' || event.key === 'Enter')) { event.preventDefault(); first.focus(); }
  });
  results.addEventListener('keydown', event => {
    const links = [...results.querySelectorAll('a')]; const at = links.indexOf(document.activeElement);
    if (event.key === 'ArrowDown' && links[at + 1]) { event.preventDefault(); links[at + 1].focus(); }
    if (event.key === 'ArrowUp') { event.preventDefault(); (links[at - 1] || input).focus(); }
  });
  if ('IntersectionObserver' in window) {
    const headings = document.querySelectorAll('.prose h2[id], .prose h3[id]');
    const observer = new IntersectionObserver(entries => {
      const first = entries.find(entry => entry.isIntersecting);
      if (!first) { return; }
      for (const link of document.querySelectorAll('.page-toc a')) {
        if (decodeURIComponent(link.hash.slice(1)) === first.target.id) { link.setAttribute('aria-current', 'location'); }
        else { link.removeAttribute('aria-current'); }
      }
    }, {rootMargin: '-80px 0px -65% 0px'});
    headings.forEach(heading => observer.observe(heading));
  }
})();
