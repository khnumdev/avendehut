(function(){
  const qs = (sel, el=document) => el.querySelector(sel);
  const qsa = (sel, el=document) => Array.from(el.querySelectorAll(sel));

  const state = {
    items: [],
    filtered: [],
    tagSet: new Set(),
    query: "",
    tags: new Set(),
    cursor: -1,
  };

  function loadData(){
    const indexPath = 'data/index.json';
    return fetch('data.json').then(r => {
      if(r.ok) return r.json().then(arr => [arr]);
      // Try chunked
      return fetch(indexPath).then(r2 => r2.json()).then(idx => Promise.all(idx.chunks.map(p => fetch(p).then(r => r.json()))));
    }).then(chunks => chunks.flat());
  }

  function renderTags(){
    const el = qs('#tags');
    el.innerHTML = '';
    Array.from(state.tagSet).sort().forEach(tag => {
      const opt = document.createElement('option');
      opt.value = tag; opt.textContent = tag;
      el.appendChild(opt);
    });
  }

  function highlight(text, query){
    if(!query) return text;
    const idx = text.toLowerCase().indexOf(query.toLowerCase());
    if(idx === -1) return text;
    return text.substring(0, idx) + '<mark>' + text.substring(idx, idx+query.length) + '</mark>' + text.substring(idx+query.length);
  }

  function render(){
    const list = qs('#results');
    list.innerHTML = '';
    const query = state.query.trim();
    const tags = state.tags;
    const filtered = state.items.filter(it => {
      const hay = [it.title||'', (it.authors||[]).join(', '), (it.tags||[]).join(' ')].join(' ').toLowerCase();
      if(query && !hay.includes(query.toLowerCase())) return false;
      if(tags.size){
        const set = new Set((it.tags||[]).map(t=>t.toLowerCase()));
        for(const t of tags){ if(!set.has(t)) return false; }
      }
      return true;
    });
    state.filtered = filtered;
    qs('#stats').textContent = `${filtered.length} result(s)`;

    // Lazy render in chunks
    const CHUNK = 100;
    let i = 0;
    function step(){
      const frag = document.createDocumentFragment();
      for(let k=0; k<CHUNK && i<filtered.length; k++, i++){
        const it = filtered[i];
        const li = document.createElement('li');
        li.className = 'card';
        li.innerHTML = `<h3>${highlight(it.title||'', query)}</h3>
          <div class="meta">${(it.authors||[]).join(', ')} ${it.published_year?('· '+it.published_year):''} · ${it.extension}</div>
          <div class="tags">${(it.tags||[]).map(t=>`<span class="tag">${t}</span>`).join('')}</div>
          <div class="meta">${it.path_rel}</div>`;
        frag.appendChild(li);
      }
      list.appendChild(frag);
      if(i < filtered.length){
        requestIdleCallback(step);
      }
    }
    step();
  }

  function applyDark(pref){
    const root = document.documentElement;
    if(pref) root.classList.add('dark'); else root.classList.remove('dark');
  }

  function initShortcuts(){
    document.addEventListener('keydown', (e) => {
      if(e.key === '/'){ e.preventDefault(); qs('#search').focus(); }
      else if(e.key === 'Escape'){ qs('#search').value=''; state.query=''; render(); }
      else if(e.key.toLowerCase() === 'd'){ const cur = localStorage.getItem('dark')==='1'; const next = !cur; localStorage.setItem('dark', next?'1':'0'); applyDark(next); }
      else if(e.key === 'j' || e.key === 'k'){ /* reserved for list navigation */ }
    });
  }

  function init(){
    const darkPref = localStorage.getItem('dark')==='1';
    applyDark(darkPref);
    initShortcuts();

    loadData().then(items => {
      state.items = items;
      items.forEach(it => (it.tags||[]).forEach(t => state.tagSet.add(String(t).toLowerCase())));
      renderTags();
      render();
    });

    qs('#search').addEventListener('input', e => { state.query = e.target.value; render(); });
    qs('#tags').addEventListener('change', e => {
      const sel = Array.from(e.target.selectedOptions).map(o=>o.value.toLowerCase());
      state.tags = new Set(sel);
      render();
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();

