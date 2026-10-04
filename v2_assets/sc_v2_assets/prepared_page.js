// Only current-page presentation. Page requests ask Python/cache for next data.
function scMarkup(text, allowHtml=false) {
  // The existing SC helpers use this Streamlit inline color extension.
  const prepared = String(text).replace(/:green-background\[([^\]\n]*)\]/g,
    '<span style="background-color:rgba(33,195,84,.1);padding:2px 6px;border-radius:4px;">$1</span>');
  return sanitizeHtml(scMarkdown.parse(prepared, {async:false, gfm:true, breaks:false,
    walkTokens(token) { if (!allowHtml && token.type === 'html') token.text = token.text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  }));
}
function appendScNodes(parent, nodes) {
  for (const node of nodes) {
    const kind = node.kind, el = document.createElement(kind === 'link' ? 'a' : kind === 'code' ? 'pre' : 'div');
    el.className = 'sc-' + kind;
    if (node.language) el.dataset.language = node.language;
    if (kind === 'columns') {
      el.style.gridTemplateColumns = node.widths.map(w => `minmax(0,${Number(w)}fr)`).join(' ');
      el.style.alignItems = node.kwargs?.vertical_alignment === 'bottom' ? 'end' : 'start';
      for (const children of node.children) {
        const col = document.createElement('div'); col.className = 'sc-column';
        appendScNodes(col, children); el.appendChild(col);
      }
    } else if (kind === 'container') {
      if (node.kwargs?.border) el.classList.add('sc-bordered');
      if (node.kwargs?.horizontal) el.classList.add('sc-horizontal');
      appendScNodes(el, node.children);
    } else if (kind === 'link') {
      el.textContent = node.label;
      if (isSafeUrl(node.url)) el.setAttribute('href', node.url);
      el.setAttribute('target', '_blank'); el.setAttribute('rel', 'noopener noreferrer');
    } else if (kind === 'code') {
      el.textContent = node.text;
    } else {
      el.innerHTML = scMarkup(node.text, Boolean(node.kwargs?.unsafe_allow_html));
    }
    parent.appendChild(el);
  }
}
export default function(component) {
  const {parentElement, data, setTriggerValue} = component;
  const root = parentElement.querySelector('[data-sc-page]');
  if (!root || data?.version !== 1) return;
  // Streamlit may run cleanup on update as well as unmount. Own precisely the
  // listeners installed by this invocation; never append duplicate listeners.
  root.__scCleanup?.();
  const previous = root.__scPage;
  const changed = previous?.data.view_id !== data.view_id;
  const state = {data, pending:false, send:setTriggerValue};
  root.__scPage = state;
  if (changed) {
    const body = document.createElement('div'); body.setAttribute('data-sc-body','');
    appendScNodes(body, data.nodes);
    const nav = document.createElement('nav'); nav.setAttribute('aria-label', 'Phân trang kết quả');
    renderPager(nav, data.page, data.total_pages);
    root.replaceChildren(body, nav);
    if (previous) requestAnimationFrame(() => {
      if (root.__scPage !== state || !root.isConnected) return;
      scrollReaderTop(root);
      root.querySelector('button[aria-current="page"]')?.focus({preventScroll:true});
    });
  } else {
    root.querySelectorAll('button').forEach(b => { b.disabled = b.dataset.disabled === 'true'; });
  }
  // Remember original disabled state so an unrelated rerun can release a pending
  // request without rebuilding the content or losing native selection.
  root.querySelectorAll('button').forEach(b => { b.dataset.disabled = String(b.disabled); });
  const onClick = event => {
    const target = event.target instanceof Element ? event.target.closest('button[data-page]') : null;
    if (!target || !root.contains(target) || target.disabled || state.pending) return;
    const page = Number(target.dataset.page);
    if (!Number.isInteger(page) || page < 1 || page > data.total_pages || page === data.page) return;
    state.pending = true;
    root.querySelectorAll('button').forEach(b => { b.disabled = true; });
    state.send('page_request', {resource_id:data.resource_id, revision:data.revision, mode:data.mode,
      view_id:data.view_id, from_page:data.page, page});
  };
  root.addEventListener('click', onClick);
  const dictCleanup = data.dictionary ? dictInstall(root, {...data.dictionary,channel:data.mode,resource_id:data.view_id}) : undefined;
  const cleanup = () => {
    root.removeEventListener('click', onClick);
    dictCleanup?.();
    if (root.__scCleanup === cleanup) delete root.__scCleanup;
  };
  root.__scCleanup = cleanup;
  return cleanup;
}
