/* Shared English popup contract. No listeners or lookup/data ownership here. */
var scappEnglishPopup = (() => {
  const config = Object.freeze({
    maxHeight: 400, margin: 12, gap: 8,
    style: Object.freeze({
      position: 'fixed', boxSizing: 'border-box', zIndex: '999999',
      background: 'var(--eng-popup-bg, var(--dl-popup-bg, #ecebe3))',
      border: '1px solid var(--eng-border, var(--dl-border, #d3d2ca))',
      boxShadow: '0 4px 18px rgba(0,0,0,0.22)', borderRadius: '4px', padding: '12px',
      color: 'var(--eng-reader-text, var(--dl-text, #3d3a2a))',
      fontFamily: 'var(--eng-reader-font, var(--dl-font-reader, "Source Sans Pro", sans-serif))',
      fontSize: 'var(--eng-reader-font-size, var(--dl-reader-font-size, 1rem))',
      lineHeight: 'var(--eng-reader-line-height, var(--dl-reader-line-height, 1.6))',
      overflowY: 'auto', overflowX: 'auto', overscrollBehavior: 'contain',
      pointerEvents: 'auto', userSelect: 'text', minHeight: '0', minWidth: '0',
      right: 'auto', bottom: 'auto', height: 'auto', transform: 'none', margin: '0'
    })
  });

  // A rect is always expressed in the popup's viewport. Never vertically clamp
  // a placed box across the target: shrink on the chosen side instead.
  function geometry(rect, width, height, viewport, options = {}) {
    const margin = Math.max(0, options.margin ?? config.margin);
    const gap = Math.max(1, options.gap ?? config.gap);
    const cap = Math.min(config.maxHeight, Math.max(0, options.maxHeight ?? config.maxHeight));
    const vw = viewport.width, vh = viewport.height;
    const availableWidth = Math.max(0, vw - 2 * margin);
    if (rect.bottom <= margin || rect.top >= vh - margin || rect.right <= 0 || rect.left >= vw || !availableWidth) return null;
    const below = Math.max(0, vh - margin - rect.bottom - gap);
    const above = Math.max(0, rect.top - gap - margin);
    const wanted = Math.min(cap, Math.max(0, height));
    const side = wanted <= below ? 'below' : wanted <= above ? 'above' : below >= above ? 'below' : 'above';
    const maxHeight = Math.min(cap, side === 'below' ? below : above);
    const actualHeight = Math.min(wanted, maxHeight);
    if (actualHeight <= 0) return null;
    const actualWidth = Math.min(Math.max(0, width), availableWidth);
    return {
      side, maxHeight, height: actualHeight, width: actualWidth,
      left: Math.max(margin, Math.min(rect.left, vw - margin - actualWidth)),
      top: side === 'below' ? rect.bottom + gap : rect.top - gap - actualHeight
    };
  }

  function targetRect(target, destinationWindow) {
    const original = target.getBoundingClientRect();
    let rect = {left: original.left, top: original.top, right: original.right, bottom: original.bottom};
    let sourceWindow = target.ownerDocument.defaultView;
    try {
      // Includes iframe border and CSS scale. The current app uses same-origin
      // iframe->ancestor popups. Unknown/cross-origin ancestry is not guessed.
      for (let depth = 0; sourceWindow !== destinationWindow; depth++) {
        if (!sourceWindow || depth >= 16) return null;
        const frame = sourceWindow.frameElement;
        if (!frame) return null;
        const box = frame.getBoundingClientRect();
        const sx = frame.offsetWidth ? box.width / frame.offsetWidth : 1;
        const sy = frame.offsetHeight ? box.height / frame.offsetHeight : 1;
        const left = box.left + (frame.clientLeft || 0) * sx;
        const top = box.top + (frame.clientTop || 0) * sy;
        rect = {left: left + rect.left*sx, right: left + rect.right*sx,
                top: top + rect.top*sy, bottom: top + rect.bottom*sy};
        sourceWindow = frame.ownerDocument.defaultView;
      }
      return rect;
    } catch (_) { return null; }
  }

  function place(popup, target, options = {}) {
    if (!popup || !target) return null;
    const doc = popup.ownerDocument;
    const win = doc.defaultView;
    const hide = () => {
      popup.style.visibility = 'hidden';
      popup.setAttribute('aria-hidden', 'true');
      return null;
    };
    const rect = targetRect(target, win);
    if (!rect) return hide();
    const viewport = {width: doc.documentElement.clientWidth || win.innerWidth,
                      height: doc.documentElement.clientHeight || win.innerHeight};
    const margin = Math.max(0, options.margin ?? config.margin);
    Object.assign(popup.style, config.style);
    popup.style.visibility = 'hidden';
    popup.style.maxHeight = config.maxHeight + 'px';
    popup.style.maxWidth = Math.max(0, viewport.width - 2*margin) + 'px';
    if (options.width) popup.style.width = Math.min(options.width, Math.max(0, viewport.width - 2*margin)) + 'px';
    popup.style.left = '0px'; popup.style.top = '0px';
    const measured = popup.getBoundingClientRect();
    let result = geometry(rect, measured.width, measured.height, viewport, options);
    if (!result) return hide();
    popup.style.maxHeight = result.maxHeight + 'px';
    // Remeasure after reducing height (border-box, padding and scrollbars).
    // A microscopic viewport may not even fit the box decoration; hide rather
    // than cross the anchor or render outside the usable viewport.
    const fitted = popup.getBoundingClientRect();
    if (fitted.height > result.maxHeight + 0.5 || fitted.width > viewport.width - 2*margin + 0.5) return hide();
    result = {...result, height:fitted.height, width:fitted.width,
      top: result.side === 'below' ? rect.bottom + Math.max(1,options.gap ?? config.gap)
           : rect.top - Math.max(1,options.gap ?? config.gap) - fitted.height};
    popup.style.left = result.left + 'px'; popup.style.top = result.top + 'px';
    popup.style.visibility = 'visible'; popup.setAttribute('aria-hidden', 'false');
    return result;
  }
  return Object.freeze({config, geometry, targetRect, place});
})();
