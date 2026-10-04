// Shared isolated-root runtime. The document bus carries only scoped local UI events.
function dictEscape(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function dictNormalize(word, language, canonical) {
  let value = String(word || '').trim().toLowerCase();
  if (language === 'en') return value.replace(/[‘’]/g, "'").replace(/^["'“”]+|["'“”]+$/g, '');
  if (!canonical) return value.replace(/[^a-zāīūṅñṭḍṇḷṃṁ\s]/gi, '').trim();
  return value.replace(/\u00ad/g, '').replace(/ṁg/g,'ṅg').replace(/ṁk/g,'ṅk').replace(/[’”'"]/g,'').replace(/ṁ/g,'ṃ');
}
function dictDecorate(root, language) {
  const rex = language === 'en' ? /\p{L}+(?:[’']\p{L}+)*(?:-\p{L}+(?:[’']\p{L}+)*)*/gu : /[^\s,.–—:;?!“‘-]+/gu;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = []; let node;
  while ((node = walker.nextNode())) {
    if (!node.parentElement?.closest('a,script,style,textarea,[data-dict-word],.pali-word,.eng-word,.eng-sub-word')) nodes.push(node);
  }
  for (const text of nodes) {
    const fragment = document.createDocumentFragment(); let cursor = 0;
    for (const match of text.textContent.matchAll(rex)) {
      fragment.append(document.createTextNode(text.textContent.slice(cursor, match.index)));
      const span = document.createElement('span'); span.dataset.dictWord = match[0]; span.dataset.dictLang = language;
      span.className = 'dict-word'; span.textContent = match[0]; fragment.append(span); cursor = match.index + match[0].length;
    }
    fragment.append(document.createTextNode(text.textContent.slice(cursor))); text.replaceWith(fragment);
  }
}
function dictDecorateDetails(root, data) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); const nodes=[]; let node;
  while ((node = walker.nextNode())) {
    const p = node.parentElement; if (!p) continue;
    const policy = data.detail_policy;
    if (p.closest('script,style,a,code,pre,th,.heading,.eng-word,.no-en-lookup,[data-dict-word]')) continue;
    if (policy === 'text' && p.closest('table,th,td')) continue;
    if (policy === 'dpd' && p.closest('b,strong,dfn,sup,.ref')) continue;
    if (policy === 'pts' && p.closest('dfn,.ref,.square,sup')) continue;
    const table = p.closest('table');
    if (table && !['text','dpd','pts'].includes(policy)) {
      if (policy === 'none') continue;
      const td = p.closest('td'); if (!td) continue;
      if (policy !== 'all_td') {
        if (table.classList.contains('family')) { if (!td.matches('td:nth-of-type(2)')) continue; }
        else if (policy === 'meaning_only') continue;
      }
    }
    nodes.push(node);
  }
  for (const text of nodes) {
    const fragment=document.createDocumentFragment(); let cursor=0, changed=false;
    for (const match of text.textContent.matchAll(/\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b/g)) {
      if (!data.en_lookup?.[match[0].toLowerCase()]) continue;
      fragment.append(document.createTextNode(text.textContent.slice(cursor,match.index)));
      const word=document.createElement('span'); word.dataset.dictWord=match[0]; word.dataset.dictLang='en'; word.className='dict-word'; word.textContent=match[0]; fragment.append(word);
      cursor=match.index+match[0].length; changed=true;
    }
    if (changed) {fragment.append(document.createTextNode(text.textContent.slice(cursor)));text.replaceWith(fragment);}
  }
}
function dictInstall(root, data, bus = document) {
  root.__dictionaryCleanup?.();
  const controller = new AbortController(); const signal = controller.signal;
  const topic = 'scapp-dictionary-r14'; let hideTimer, frame, popup, englishPopup, active;
  let activePaint;
  root.dataset.dictionarySurface = data.role === 'panel' ? 'sidebar' :
    [data.pali_position, data.english_position].includes('left') ? 'left' : 'content';
  function clearActive() {
    if (!active) return;
    active.classList.remove('dict-active');
    for (const [name, value, priority] of activePaint || []) {
      if (value) active.style.setProperty(name, value, priority); else active.style.removeProperty(name);
    }
    active = null; activePaint = null;
  }
  function activate(target, language) {
    if (target === active) return;
    clearActive(); active = target; active.classList.add('dict-active');
    // Inline paint priority deliberately beats glossary !important selectors.
    // Preserve/restore original paint; do not change border widths or metrics.
    activePaint = ['background-color', 'color', 'border-bottom-color'].map(name =>
      [name, target.style.getPropertyValue(name), target.style.getPropertyPriority(name)]);
    const color = language === 'pi' ? 'var(--dl-pali,#d63031)' : 'var(--dl-en,#5d7367)';
    target.style.setProperty('background-color', 'var(--dl-bg-hover,#ecebe3)', 'important');
    target.style.setProperty('color', color, 'important');
    target.style.setProperty('border-bottom-color', color, 'important');
  }
  function panelDecorations(meaning) {
    // Generated dictionary HTML can paint a hardcoded main surface and a final
    // inline border. Mark its real terminal block chain, not every descendant.
    const sample = document.createElement('span');
    sample.style.backgroundColor = getComputedStyle(root).getPropertyValue('--dict-main-surface').trim();
    if (sample.style.backgroundColor) for (const el of meaning.querySelectorAll('*')) {
      if (getComputedStyle(el).backgroundColor === sample.style.backgroundColor)
        el.dataset.dictNeutralSurface = '';
    }
    function terminal(node) {
      if (node instanceof Element && node.matches('div,section,article')) node.dataset.dictTerminalWrapper = '';
      const children = [...node.childNodes].filter(child =>
        child.nodeType === Node.TEXT_NODE ? !!child.textContent.trim() :
        child instanceof Element && (child.tagName === 'HR' || !!child.textContent.trim()));
      while (children.at(-1) instanceof Element && children.at(-1).tagName === 'HR')
        children.pop().dataset.dictTerminalRule = '';
      const last = children.at(-1);
      if (last instanceof Element && last.matches('div,section,article')) terminal(last);
    }
    terminal(meaning);
  }
  const subscribe = (target, name, listener) => target.addEventListener(name, listener, {signal});
  const send = detail => bus.dispatchEvent(new CustomEvent(topic, {detail:{...detail, channel:data.channel, resource:data.resource_id}}));
  const accepted = detail => detail?.channel === data.channel && detail?.resource === data.resource_id;
  const lookup = (word, lang) => {
    const values = lang === 'en' ? data.en_lookup : data.pali_lookup;
    return values?.[dictNormalize(word, lang, data.canonical)] || values?.[word] || '';
  };
  const destination = lang => lang === 'en' ? data.english_position : data.pali_position;
  function setPanelVisible(visible) {
    if (data.role !== 'panel') return;
    root.hidden = !visible;
    root.style.height = visible ? `${data.height}px` : '0px';
    if (data.legacy_panel_frame) {
      try {
        window.parent.postMessage({
          isStreamlitMessage: true,
          type: 'streamlit:setFrameHeight',
          height: visible ? data.height : 0
        }, '*');
      } catch (_) {}
    }
  }
  function closePopup() { if (popup) popup.hidden = true; if (englishPopup) englishPopup.hidden = true; }
  function fill(box, entry, popupMode = false) {
    if (!box) return;
    const meaning = document.createElement('div'); meaning.dataset.dictionaryMeaning = '';
    meaning.innerHTML = sanitizeHtml(entry.meaning || 'Không tìm thấy trong từ điển.');
    // Popup content stays simple like the legacy lookup popup: no extra heading,
    // nested padding, or bottom separator. Panels keep their existing history UI.
    if (entry.lang === 'pi' && data.meaning_english) dictDecorate(meaning, 'en');
    if (popupMode) {
      box.replaceChildren(meaning);
      box.scrollTop = 0;
      return;
    }
    const item = document.createElement('div'); item.className = 'dict-entry';
    const heading = document.createElement('strong'); heading.textContent = entry.word;
    item.append(heading, meaning);
    if (data.history && entry.lang === 'pi') box.append(item); else box.replaceChildren(item);
    panelDecorations(meaning);
    // Dictionary panels always show a newly selected entry from its beginning.
    box.scrollTop = 0;
  }
  function receive(event) {
    const d = event.detail; if (!accepted(d)) return;
    if (d.kind === 'entry') {
      fill(root.querySelector(`[data-dict-panel="${d.lang}"]`), d);
      setPanelVisible(true);
    }
    if (d.kind === 'reset') {
      root.querySelectorAll('[data-dict-panel]').forEach(e => e.replaceChildren());
      setPanelVisible(false);
      closePopup();
    }
  }
  subscribe(bus, topic, receive);
  function showPopup(target, entry) {
    clearTimeout(hideTimer);
    if (entry.lang === 'en') {
      if (!englishPopup) {
        englishPopup = document.createElement('div'); englishPopup.className = 'dict-popup dict-popup-english'; englishPopup.setAttribute('role','tooltip'); root.append(englishPopup);
        subscribe(englishPopup, 'mouseenter', () => clearTimeout(hideTimer));
        subscribe(englishPopup, 'mouseleave', () => { hideTimer = setTimeout(closePopup, 140); });
      }
      fill(englishPopup, entry, true); englishPopup.hidden = false;
      scappEnglishPopup.place(englishPopup, target, {width: 550});
      englishPopup.scrollTop = 0;
      return;
    }
    if (englishPopup) englishPopup.hidden = true;
    if (!popup) {
      popup = document.createElement('div'); popup.className = 'dict-popup dict-popup-pali'; popup.setAttribute('role','tooltip'); root.append(popup);
      subscribe(popup, 'mouseenter', () => clearTimeout(hideTimer));
      subscribe(popup, 'mouseleave', () => { hideTimer = setTimeout(closePopup, 140); });
    }
    fill(popup, entry, true); popup.hidden = false;
    // Preserve the pre-R14 Pāli popup geometry instead of sharing the English
    // contract. This intentionally mirrors the existing viewport adapter.
    const viewportWidth = document.documentElement.clientWidth || window.innerWidth;
    const viewportHeight = document.documentElement.clientHeight || window.innerHeight;
    const rect = target.getBoundingClientRect();
    const margin = 12, gap = 8;
    const clamp = (value, minValue, maxValue) => maxValue < minValue ? minValue : Math.min(Math.max(value, minValue), maxValue);
    popup.style.position = 'fixed'; popup.style.left = '0px'; popup.style.top = '0px';
    popup.style.right = 'auto'; popup.style.bottom = 'auto'; popup.style.width = 'auto';
    popup.style.maxHeight = Math.max(80, viewportHeight - margin * 2) + 'px';
    popup.style.visibility = 'hidden';
    const popupRect = popup.getBoundingClientRect();
    const popupWidth = Math.min(popupRect.width, Math.max(0, viewportWidth - margin * 2));
    const popupHeight = Math.min(popupRect.height, Math.max(0, viewportHeight - margin * 2));
    const spaceAbove = rect.top - gap - margin;
    const spaceBelow = viewportHeight - rect.bottom - gap - margin;
    const placeBelow = popupHeight <= spaceBelow ? true : popupHeight <= spaceAbove ? false : spaceBelow >= spaceAbove;
    const left = clamp(rect.left, margin, viewportWidth - margin - popupWidth);
    let top = placeBelow ? rect.bottom + gap : rect.top - gap - popupHeight;
    top = clamp(top, margin, viewportHeight - margin - popupHeight);
    popup.style.left = Math.round(left) + 'px'; popup.style.top = Math.round(top) + 'px';
    popup.style.visibility = 'visible'; popup.scrollTop = 0;
  }
  function targetOf(event) {
    const el = event.target instanceof Element ? event.target.closest('[data-dict-word],.pali-word,.eng-word,.eng-sub-word') : null;
    return el && root.contains(el) && !el.closest('a') ? el : null;
  }
  function entryOf(target) {
    const lang = target.dataset.dictLang || (target.matches('.pali-word') ? 'pi' : 'en');
    const word = target.dataset.dictWord || target.dataset.clean || target.dataset.word || target.textContent;
    return {kind:'entry', lang, word, meaning:lookup(word,lang)};
  }
  subscribe(root, 'mouseover', event => {
    const target = targetOf(event); if (!target || (event.relatedTarget instanceof Node && target.contains(event.relatedTarget))) return;
    const entry = entryOf(target);
    activate(target, entry.lang);
    if (entry.lang === "pi" && data.hover_lookup) entry.meaning = data.hover_lookup[dictNormalize(entry.word,"pi",data.canonical)] || data.hover_lookup[entry.word] || "";
    if (data.hover_popup || destination(entry.lang) === 'popup') showPopup(target, entry);
  });
  subscribe(root, 'mouseout', event => {
    if (targetOf(event)) hideTimer = setTimeout(closePopup, 140);
  });
  subscribe(root, 'click', event => {
    const target = targetOf(event); if (!target) return;
    const entry = entryOf(target); if (entry.lang === 'en' && data.english_hover_only) return;
    activate(target, entry.lang);
    if (destination(entry.lang) === 'popup') showPopup(target, entry); else { closePopup(); send(entry); }
  });
  subscribe(document, 'pointerdown', event => { if (!event.composedPath().includes(root)) closePopup(); });
  subscribe(document, 'keydown', event => { if (event.key === 'Escape') closePopup(); });
  subscribe(window, 'resize', closePopup);
  subscribe(root, 'scroll', closePopup);
  if (data.role !== 'panel' && !data.predecorated) {
    root.querySelectorAll('[lang="pi"],[lang="pli"],[lang="pali"],[data-language="pi"],[data-language="pli"]').forEach(el => {
      if (!el.parentElement?.closest('[lang="pi"],[lang="pli"],[lang="pali"],[data-language="pi"],[data-language="pli"]')) dictDecorate(el,'pi');
    });
    root.querySelectorAll('[lang="en"],[data-language="en"]').forEach(el => {
      if (!el.parentElement?.closest('[lang="en"],[data-language="en"]')) dictDecorate(el,'en');
    });
  }
  if (data.detail_policy && data.role !== 'panel' && !data.predecorated) dictDecorateDetails(root.querySelector('.dict-content') || root, data);
  const scroller = root.querySelector('.chanting-text-col');
  if (scroller && data.auto_scroll_speed > 0) {
    let pauseUntil=0, last=0, position=scroller.scrollTop;
    const pause = () => {pauseUntil=performance.now()+1500; position=scroller.scrollTop;};
    for (const name of ['wheel','touchstart','touchmove','pointerdown']) subscribe(scroller,name,pause);
    subscribe(scroller,'keydown', e => {if (['ArrowDown','ArrowUp','PageDown','PageUp','Home','End',' '].includes(e.key)) pause();});
    const tick = now => {
      const delta=Math.min(100,now-(last || now));last=now;
      if(now >= pauseUntil) {position += data.auto_scroll_speed*delta/1000;scroller.scrollTop=position;}
      if(scroller.scrollTop < scroller.scrollHeight-scroller.clientHeight-1) frame=requestAnimationFrame(tick);
    };
    frame=requestAnimationFrame(tick);
  }
  // All listeners/timers/popup are released on unmount or resource replacement.
  const cleanup = () => { controller.abort(); clearTimeout(hideTimer); cancelAnimationFrame(frame); popup?.remove(); englishPopup?.remove(); clearActive(); };
  root.__dictionaryCleanup = cleanup; return cleanup;
}
export default function(component) {
  const root = component.parentElement.querySelector('[data-dictionary-root]'); const data = component.data;
  if (!root || data?.version !== 1) return;
  root.__dictionaryCleanup?.();
  const style = document.createElement('style'); style.textContent = data.css;
  const layout = document.createElement('div'); layout.className = 'dict-layout';
  if (data.role === 'panel') {
    const panel = document.createElement('aside'); panel.dataset.dictPanel = data.panel_language; panel.style.flex='1'; layout.append(panel);
  } else {
    const left = document.createElement('div'); left.className='dict-left';
    for (const [lang, position] of [['pi',data.pali_position],['en',data.english_position]]) if (position === 'left') {
      const panel = document.createElement('aside'); panel.dataset.dictPanel = lang; left.append(panel);
    }
    if (left.childElementCount) layout.append(left);
    const body = document.createElement('div'); body.className = 'dict-content text-container'; body.innerHTML = sanitizeHtml(data.markdown ? dictionaryMarkdown.parse(data.body_html, {walkTokens(token){if(!data.allow_html && token.type==='html') token.text=token.text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}}) : data.body_html); layout.append(body);
  }
  if (data.role === 'panel') {
    root.hidden = true;
    root.style.height = '0px';
  } else {
    root.hidden = false;
    root.style.height = `${data.height}px`;
  }
  root.replaceChildren(style,layout);
  root.__panelState = data;
  if (data.highlight_word && typeof applyReaderKeywordHighlight === 'function') applyReaderKeywordHighlight(root);
  return dictInstall(root,data);
}
