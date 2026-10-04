// DPD section toggles are DOM-only. Dictionary events/geometry stay shared.
function dpdDecorate(body, data) {
  const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT);
  const nodes = []; let node;
  while ((node = walker.nextNode())) {
    const p = node.parentElement;
    if (!p || p.closest('button,a,script,style,code,pre,select,option,textarea,[data-dpd-no-lookup],[data-dict-word]')) continue;
    if (!/\p{L}/u.test(node.textContent)) continue;
    nodes.push(node);
  }
  for (const text of nodes) {
    const p = text.parentElement;
    const marker = p.closest('[data-dpd-language],[lang]');
    let language = marker?.dataset.dpdLanguage || marker?.getAttribute('lang') || 'mixed';
    if (language === 'none') continue;
    // Mixed precomputed DPD family tables have lemma and meaning columns.
    const cell = p.closest('td,th');
    if (language === 'mixed' && cell?.closest('table.family')) {
      if (cell.tagName === 'TH') continue;
      const index = Array.from(cell.parentElement.children).indexOf(cell);
      language = index === 0 ? 'pi' : index === 1 ? 'en' : 'mixed';
    }
    const regex = /\p{L}+(?:[’']\p{L}+)*(?:-\p{L}+(?:[’']\p{L}+)*)*/gu;
    const fragment = document.createDocumentFragment(); let cursor = 0, changed = false;
    for (const match of text.textContent.matchAll(regex)) {
      const word = match[0];
      const pi = data.pali_lookup?.[dictNormalize(word, 'pi', true)];
      const en = data.en_lookup?.[dictNormalize(word, 'en', true)];
      const lang = ['pi','pli','pali'].includes(language) ? (pi ? 'pi' : null) :
        language === 'en' ? (en ? 'en' : null) : pi ? 'pi' : en ? 'en' : null;
      if (!lang) continue;
      fragment.append(document.createTextNode(text.textContent.slice(cursor, match.index)));
      const span = document.createElement('span'); span.className = 'dict-word';
      span.dataset.dictWord = word; span.dataset.dictLang = lang; span.textContent = word;
      fragment.append(span); cursor = match.index + word.length; changed = true;
    }
    if (changed) {fragment.append(document.createTextNode(text.textContent.slice(cursor))); text.replaceWith(fragment);}
  }
}
function dpdSanitize(raw, fragments) {
  // Database HTML travels separately from the escaped structural skeleton;
  // it cannot break out of its region and forge a control/script sibling.
  const template = document.createElement('template'); template.innerHTML = raw;
  for (const region of template.content.querySelectorAll('[data-dpd-html]')) {
    region.innerHTML = sanitizeHtml(fragments[region.dataset.dpdHtml]?.html || '');
  }
  return template.content;
}
export default function(component) {
  const root = component.parentElement.querySelector('[data-dpd-root]'); const data = component.data;
  if (!root || data?.version !== 1) return;
  root.__dpdCleanup?.();
  if (root.__dpdResource !== data.resource_id) {
    const style = document.createElement('style'); style.textContent = data.css;
    const layout = document.createElement('div'); layout.className = 'dict-layout';
    const left = document.createElement('div'); left.className = 'dict-left'; left.hidden = true;
    for (const [lang, position] of [['pi',data.pali_position],['en',data.english_position]]) if (position === 'left') {
      const panel = document.createElement('aside'); panel.dataset.dictPanel = lang; left.append(panel);
    }
    if (left.childElementCount) layout.append(left);
    const body = document.createElement('div'); body.className = 'dict-content';
    body.append(dpdSanitize(data.body_html, data.fragments)); layout.append(body);
    root.replaceChildren(style, layout); root.__dpdResource = data.resource_id;
    dpdDecorate(body, data); root.scrollTop = 0;
  }
  root.style.height = 'auto';
  const controller = new AbortController(); const signal = controller.signal;
  const installCleanup = dictInstall(root, data);
  const left = root.querySelector('.dict-left');
  const updateLeft = () => {if (left) left.hidden = !Array.from(left.querySelectorAll('[data-dict-panel]')).some(p => p.childElementCount);};
  const observer = new MutationObserver(updateLeft);
  if (left) observer.observe(left, {childList:true,subtree:true});
  updateLeft();
  root.addEventListener('click', event => {
    const button = event.target instanceof Element ? event.target.closest('button') : null;
    if (!button || !root.contains(button)) return;
    if (button.dataset.dpdSelect !== undefined) {
      root.querySelectorAll('[data-dpd-entry]').forEach(entry => {entry.hidden = entry.dataset.dpdEntry !== button.dataset.dpdSelect;});
      root.querySelectorAll('button[data-dpd-select]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.dpdSelect === button.dataset.dpdSelect)));
    } else if (button.dataset.dpdToggle) {
      const section = Array.from(root.querySelectorAll('[data-dpd-section]')).find(s => s.dataset.dpdSection === button.dataset.dpdToggle);
      if (section) {section.hidden = !section.hidden; button.setAttribute('aria-expanded', String(!section.hidden));}
    }
    // Intrinsic content height + Streamlit v2's content ResizeObserver handle
    // every expansion/collapse without state/trigger calls or Python reruns.
  }, {signal});
  const cleanup = () => {controller.abort(); observer.disconnect(); installCleanup();};
  root.__dpdCleanup = cleanup;
  return cleanup;
}
