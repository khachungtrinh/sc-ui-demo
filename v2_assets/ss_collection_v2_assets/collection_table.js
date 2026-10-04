// Structured resource; all dynamic strings use textContent, never an HTML sink.
function safeHref(value) {
  if (typeof value !== "string" || /[\x00-\x1f\\]/.test(value)) return null;
  try {
    const url = new URL(value, window.location.origin);
    if (value.startsWith("/ss?uid=") && url.origin === window.location.origin && url.pathname === "/ss") return value;
    if (url.protocol === "https:" && url.host === "suttacentral.net" && value.startsWith("https://suttacentral.net/")) return value;
  } catch (_) { /* invalid href stays text */ }
  return null;
}
function node(tag, text, className) {
  const result = document.createElement(tag);
  if (text !== undefined) result.textContent = String(text ?? "");
  if (className) result.className = className;
  return result;
}
function appendIdentity(cell, uid, resource, mode, primary) {
  const link = resource.links[uid] || {label: uid};
  const href = mode === "text" ? null : safeHref(link[mode + "_href"]);
  const element = node(href ? "a" : "span", link.label, primary ? "ss-uid" : "");
  if (href) {
    element.setAttribute("href", href);
    element.setAttribute("target", "_blank");
    element.setAttribute("rel", "noopener noreferrer");
  }
  cell.appendChild(element);
}
export default function(component) {
  const {parentElement, data: resource} = component;
  const root = parentElement.querySelector("[data-ss-collection-root]");
  if (!root || resource?.schema_version !== 1) return;
  const previous = root.__ssCollectionView;
  if (previous?.cleanup) previous.cleanup();
  const state = previous || {};
  const identity = resource.resource_id + ":" + resource.revision;
  if (state.identity !== identity) {
    state.identity = identity;
    state.collection = resource.default_collection;
    state.mode = resource.default_display_mode;
  }
  const modes = resource.display_modes;
  if (!resource.collection_order.includes(state.collection)) state.collection = resource.default_collection;
  if (!modes.some(item => item.id === state.mode)) state.mode = resource.default_display_mode;
  root.replaceChildren();
  root.appendChild(node("h2", resource.heading));
  const controls = node("div", undefined, "ss-controls");
  // Taisho-style app-owned menus; every gesture/choice remains browser-local.
  const off = [], menus = [];
  const listen = (element, type, callback) => {
    element.addEventListener(type, callback);
    off.push(() => element.removeEventListener(type, callback));
  };
  function closeMenus(restoreFocus = false) {
    for (const menu of menus) {
      const wasOpen = !menu.list.hidden;
      menu.list.hidden = true;
      menu.button.setAttribute("aria-expanded", "false");
      if (restoreFocus && wasOpen) menu.button.focus();
    }
  }
  function chooser(labelText, values, initialValue, onChange) {
    const control = node("div"), label = node("div", labelText, "ss-control-label");
    const group = node("div", undefined, "ss-select");
    const button = node("button"), text = node("span", "", "ss-select-label");
    button.type = "button";
    button.setAttribute("data-scapp-control", "select");
    button.setAttribute("role", "combobox");
    button.setAttribute("aria-label", labelText);
    button.setAttribute("aria-haspopup", "listbox");
    button.setAttribute("aria-expanded", "false");
    const chevron = node("span", undefined, "ss-chevron");
    chevron.setAttribute("aria-hidden", "true");
    button.append(text, chevron);
    const list = node("div", undefined, "ss-options");
    list.setAttribute("role", "listbox");
    list.setAttribute("aria-label", labelText);
    list.id = "ss-choice-" + Math.random().toString(36).slice(2);
    button.setAttribute("aria-controls", list.id);
    list.hidden = true;
    let value = initialValue, typed = "", typedAt = 0;
    const options = [];
    const update = () => {
      text.textContent = values.find(item => item.id === value)?.label ?? "";
      text.title = text.textContent;
      options.forEach((option, index) => option.setAttribute("aria-selected", String(values[index].id === value)));
    };
    const focus = index => options[(index + options.length) % options.length]?.focus();
    const open = index => {
      closeMenus();
      list.hidden = false;
      button.setAttribute("aria-expanded", "true");
      focus(index);
    };
    const choose = next => {
      value = next;
      update();
      closeMenus();
      button.focus();
      onChange(next);
    };
    const findTyped = event => {
      if (event.ctrlKey || event.metaKey || event.altKey || event.key.length !== 1 || event.key === " ") return false;
      const now = Date.now();
      typed = (now - typedAt > 1000 ? "" : typed) + event.key.toLocaleLowerCase();
      typedAt = now;
      let index = values.findIndex(item => item.label.toLocaleLowerCase().startsWith(typed));
      if (index < 0) { typed = event.key.toLocaleLowerCase(); index = values.findIndex(item => item.label.toLocaleLowerCase().startsWith(typed)); }
      if (index >= 0) { event.preventDefault(); open(index); }
      return index >= 0;
    };
    values.forEach((item, index) => {
      const option = node("button", item.label);
      option.type = "button";
      option.setAttribute("data-scapp-option", "");
      option.setAttribute("role", "option");
      listen(option, "click", () => choose(item.id));
      listen(option, "keydown", event => {
        const move = {ArrowDown: index + 1, ArrowUp: index - 1, Home: 0, End: options.length - 1}[event.key];
        if (move !== undefined) { event.preventDefault(); event.stopPropagation(); focus(move); }
        else if (event.key === "Enter" || event.key === " ") { event.preventDefault(); event.stopPropagation(); choose(item.id); }
        else if (event.key === "Escape") { event.preventDefault(); event.stopPropagation(); closeMenus(true); }
        else if (event.key === "Tab") closeMenus();
        else findTyped(event);
      });
      list.append(option); options.push(option);
    });
    listen(button, "click", () => { if (list.hidden) open(Math.max(0, values.findIndex(item => item.id === value))); else closeMenus(); });
    listen(button, "keydown", event => {
      if (["ArrowDown", "ArrowUp", "Enter", " "].includes(event.key)) {
        event.preventDefault();
        if (event.key === "Enter" || event.key === " ") button.click();
        else open(Math.max(0, values.findIndex(item => item.id === value)));
      } else if (event.key === "Escape") { event.preventDefault(); closeMenus(true); }
      else findTyped(event);
    });
    update(); menus.push({list, button}); group.append(button, list); control.append(label, group); return control;
  }
  controls.append(
    chooser("Chế độ hiển thị:", modes, state.mode, value => { state.mode = value; draw(); }),
    chooser("Chọn bộ kinh:", resource.collection_order.map(id => ({id, label: resource.collections[id].label})),
      state.collection, value => { state.collection = value; draw(); viewport.scrollTop = 0; })
  );
  root.appendChild(controls);
  const statistics = node("p", "", "ss-statistics");
  statistics.setAttribute("role", "status");
  root.appendChild(statistics);
  const warning = node("p", "Không tìm thấy dữ liệu cho bộ kinh này.", "ss-empty");
  root.appendChild(warning);
  const viewport = node("div", undefined, "ss-table-viewport");
  viewport.setAttribute("tabindex", "0");
  viewport.setAttribute("aria-label", "Bảng dữ liệu song song");
  const table = node("table");
  table.setAttribute("data-scapp-table", "");
  const caption = node("caption");
  table.appendChild(caption);
  const head = node("thead");
  const headings = node("tr");
  // Preserve the baseline unnamed zero-based row index.
  const indexHeader = node("th", "");
  indexHeader.setAttribute("aria-label", "Chỉ số dòng");
  headings.appendChild(indexHeader);
  resource.columns.forEach(text => {
    const cell = node("th", text);
    cell.setAttribute("scope", "col");
    headings.appendChild(cell);
  });
  head.appendChild(headings);
  table.appendChild(head);
  const body = node("tbody");
  table.appendChild(body);
  viewport.appendChild(table);
  root.appendChild(viewport);
  const draw = () => {
    const collection = resource.collections[state.collection];
    const rows = collection.rows;
    const stats = collection.statistics;
    let text = `Có song song: ${stats.count_with_parallels} | Tổng số: ${stats.total_in_collection}`;
    if (stats.total_in_collection > 0) text += ` | Tỷ lệ: ${stats.percentage.toFixed(2)}%`;
    statistics.textContent = text;
    warning.hidden = Boolean(rows.length);
    viewport.hidden = !rows.length;
    caption.textContent = collection.label;
    const fragment = document.createDocumentFragment();
    rows.forEach((row, index) => {
      const tr = node("tr");
      const rowIndex = node("th", index, "ss-row-index");
      rowIndex.setAttribute("scope", "row");
      tr.appendChild(rowIndex);
      const uid = node("td");
      appendIdentity(uid, row.sutta_id, resource, state.mode, true);
      tr.appendChild(uid);
      tr.appendChild(node("td", row.title_pali));
      tr.appendChild(node("td", row.description));
      tr.appendChild(node("td", row.irff_tag));
      const parallels = node("td");
      row.parallels.forEach((parallelId, i) => {
        if (i) parallels.appendChild(document.createTextNode(", "));
        appendIdentity(parallels, parallelId, resource, state.mode, false);
      });
      tr.appendChild(parallels);
      fragment.appendChild(tr);
    });
    body.replaceChildren(fragment);
  };
  const ownerDocument = root.ownerDocument || document;
  listen(ownerDocument, "pointerdown", event => {
    const inside = event.composedPath ? event.composedPath().includes(root) : root.contains(event.target);
    if (!inside) closeMenus();
  });
  listen(root, "keydown", event => { if (event.key === "Escape") closeMenus(true); });
  draw();
  let cleaned = false;
  state.cleanup = () => {
    if (cleaned) return;
    cleaned = true;
    closeMenus();
    off.splice(0).forEach(remove => remove());
  };
  root.__ssCollectionView = state;
  return state.cleanup;
}
