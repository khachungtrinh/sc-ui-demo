function readingLabel(host,text,visible=true) {
  if(!visible) return;
  const label=document.createElement('label');label.className='reading-label';label.textContent=text;host.append(label);return label;
}
function readingCaption(node,label) {
  const parts=String(label||'').split(/(:material\/[a-z_]+:)/g);
  for(const part of parts) {
    if(part.startsWith(':material/')) {const icon=document.createElement('span');icon.className='reading-icon';icon.textContent=part.slice(10,-1);icon.setAttribute('aria-hidden','true');node.append(icon);}
    else node.append(document.createTextNode(part.replace(/\*\*/g,'')));
  }
}
function readingCopy(root,text,selectionNode) {
  const selectFullText=()=>{
    if(root.cleaned) return;
    // JSON tree labels aren't a valid JSON copy. Keep the complete canonical
    // text selected in this root's own buffer when Clipboard API is unavailable.
    root.copyBuffer?.remove();const buffer=document.createElement('textarea');
    buffer.value=text;buffer.setAttribute('aria-label','Copy text');buffer.style.cssText='position:fixed;left:-10000px;top:0;width:1px;height:1px';
    root.host.append(buffer);root.copyBuffer=buffer;buffer.focus({preventScroll:true});buffer.select();
    root.notice('Nhấn Ctrl+C để sao chép phần đã chọn.');
  };
  if(navigator.clipboard?.writeText) navigator.clipboard.writeText(text).catch(selectFullText);
  else selectFullText();
}
function readingDisplay(host,resource,root) {
  if(resource.type==='reader') return readingDictionary(host,resource.dictionary);
  if(resource.type==='read_pair') {
    const columns=document.createElement('div');columns.className='reading-columns';host.append(columns);
    const a=document.createElement('div'),b=document.createElement('div');columns.append(a,b);
    const clean=readingDictionary(a,resource.dictionary);
    if(resource.mt.rows?.length) readingDisplay(b,resource.mt,root);
    else {const msg=document.createElement('div');msg.className='reading-error';msg.textContent=resource.empty_message; b.append(msg);}
    return clean;
  }
  if(resource.type==='table') {
    const wrap=document.createElement('div');wrap.className='reading-table-wrap';wrap.style.height=`${resource.height}px`;
    const table=document.createElement('table');table.className='reading-table';
    const body=document.createElement('tbody');
    for(const row of resource.rows) {const tr=document.createElement('tr');for(const cell of row){const td=document.createElement('td');td.textContent=cell;tr.append(td);}body.append(tr);}
    table.append(body);wrap.append(table);host.append(wrap);return;
  }
  if(resource.type==='json') {
    const tree=document.createElement('div');tree.className='reading-json';
    const copy=document.createElement('button');copy.className='reading-button reading-copy';readingCaption(copy,':material/content_copy:');copy.setAttribute('aria-label','Copy JSON');copy.title='Copy JSON';
    copy.addEventListener('click',()=>readingCopy(root,JSON.stringify(resource.value,null,2),tree),{signal:root.controller.signal});
    const wrap=document.createElement('div');wrap.style.position='relative';wrap.append(copy,tree);
    function entry(parent,key,value) {
      if(value!==null && typeof value==='object') {
        const detail=document.createElement('details');detail.open=resource.expanded;const summary=document.createElement('summary');summary.textContent=`${key} ${Array.isArray(value)?'[':'{'}${Object.keys(value).length}${Array.isArray(value)?']':'}'}`;detail.append(summary);
        for(const [k,v] of Object.entries(value)) entry(detail,k,v);parent.append(detail);
      } else {const row=document.createElement('pre');row.textContent=`${key}: ${JSON.stringify(value)}`;parent.append(row);}
    }
    entry(tree,'',resource.value);host.append(wrap);return;
  }
  if(resource.type==='text_preview') {
    readingLabel(host,resource.label,resource.visible!==false);
    const text=document.createElement('textarea');text.className='reading-input';text.value=resource.value;text.disabled=true;text.style.height=`${resource.height}px`;text.setAttribute('aria-label',resource.label||'Nội dung');host.append(text);return;
  }
  if(resource.type==='code') {
    const wrap=document.createElement('div');wrap.className='reading-code-wrap';const pre=document.createElement('pre');pre.className='reading-code';pre.style.height=`${resource.height}px`;pre.textContent=resource.value;
    const button=document.createElement('button');button.className='reading-button reading-copy';readingCaption(button,':material/content_copy:');button.setAttribute('aria-label','Copy to clipboard');button.title='Copy to clipboard';button.addEventListener('click',()=>{readingCopy(root,resource.value,pre);},{signal:root.controller.signal});wrap.append(pre,button);host.append(wrap);return;
  }
  throw new Error('unsupported_shape');
}
function readingResource(root,id,provided) {
  readingStoreResource(root.scope,id,provided);
  const cached=root.scope.resources.get(id)?.value;
  if(!cached && !root.requested.has(id)) {
    root.requested.add(id);readingCommand(root,'request_resource',{resource_id:id});
  }
  return cached;
}
function readingBuildControl(root) {
  const host=root.host,widget=root.data.widget;
  readingLabel(host,widget.label,widget.label_visibility!=='collapsed' && widget.type!=='toggle' && widget.type!=='button' && widget.type!=='menu' && widget.type!=='tabs');
  let el;
  if(widget.type==='button') {
    el=document.createElement('button');el.className='reading-button'+(widget.primary?' primary':'');
    if(widget.icon) readingCaption(el,widget.icon);readingCaption(el,widget.label);
    el.addEventListener('click',()=>readingCommand(root,widget.kind),{signal:root.controller.signal});
  } else if(widget.type==='menu') {
    const menu=document.createElement('details');menu.style.position='relative';
    const summary=document.createElement('summary');summary.className='reading-button';summary.style.listStyle='none';
    if(widget.icon) readingCaption(summary,widget.icon);readingCaption(summary,widget.label);menu.append(summary);
    const list=document.createElement('div');list.style.cssText='position:absolute;z-index:20;right:0;min-width:100%;padding:4px;background:var(--st-secondary-background-color,#ecebe3);border:1px solid #d3d2ca';
    for(const choice of widget.options) {const item=document.createElement('button');item.className='reading-button';item.textContent=choice;item.disabled=widget.disabled;
      item.addEventListener('click',()=>{menu.open=false;readingCommand(root,widget.kind,{choice});},{signal:root.controller.signal});list.append(item);}
    menu.append(list);el=menu;
  } else if(widget.type==='tabs') {
    el=document.createElement('div');el.className='reading-tabs';el.setAttribute('role','tablist');
    const field=readingField(root.scope,root.data.field);root.field=field;root.tabButtons=new Map();
    for(const value of widget.options) {const b=document.createElement('button');b.className='reading-tab';b.setAttribute('role','tab');b.setAttribute('aria-selected',String(field.value===value));readingCaption(b,value);b.disabled=widget.disabled;
      b.addEventListener('click',()=>{field.value=value;field.edit_sequence++;field.dirty=true;readingPersist(root.scope,field);readingCommand(root,widget.kind);},{signal:root.controller.signal});el.append(b);root.tabButtons.set(value,b);}
  } else if(widget.type==='select') {
    el=document.createElement('select');el.className='reading-select';
    for(const [i,value] of widget.options.entries()) {const option=document.createElement('option');option.value=String(i);option.textContent=value===null?(widget.placeholder||'Choose an option'):value;el.append(option);}
  } else if(widget.type==='toggle') {
    el=document.createElement('button');el.type='button';el.className='reading-toggle-button';readingCaption(el,widget.label);
  } else {
    el=document.createElement(widget.type==='textarea'?'textarea':'input');el.className='reading-input';
    if(widget.type==='number') {el.type='number';el.min=widget.min_value;el.max=widget.max_value;el.step=widget.step;}
    if(widget.height) el.style.height=`${widget.height}px`;
    el.placeholder=widget.placeholder||'';
  }
  host.append(el);
  el.disabled=widget.disabled;el.title=widget.help||'';el.setAttribute('aria-label',widget.label||'Reading');root.element=el;
  if(root.data.field && widget.type!=='tabs') {
    const field=readingField(root.scope,root.data.field);root.field=field;
    if(widget.type==='select') {
      const selected=widget.options.indexOf(field.value);el.value=String(Math.max(0,selected));
      el.addEventListener('change',()=>{const value=widget.options[Number(el.value)];if(value!==field.value){field.value=value;field.edit_sequence++;field.dirty=true;readingPersist(root.scope,field);}field.dirty=true;readingCommand(root,widget.kind);},{signal:root.controller.signal});
    } else if(widget.type==='toggle') {
      el.setAttribute('aria-pressed',String(!!field.value));
      if(!widget.disabled) el.addEventListener('click',()=>{
        field.value=!field.value;field.edit_sequence++;field.dirty=true;
        el.setAttribute('aria-pressed',String(!!field.value));
        readingPersist(root.scope,field);readingCommand(root,widget.kind);
      },{signal:root.controller.signal});
    } else {
      el.value=field.value??'';
      if(!widget.disabled) readingBindEditor(root,el,field,widget.kind);
    }
  }
}
function readingUpdate(root,data) {
  root.data=data;root.scope.sequence=Math.max(root.scope.sequence,data.sequence_floor||0);readingAck(root.scope,data.ack);
  if(data.type==='ack') return;
  if(data.type==='control') {
    if(data.field && !root.element) {
      if(Object.hasOwn(data.field,'value')) {root.host.replaceChildren();readingBuildControl(root);}
      else {if(!root.requested.has(data.field.resource_id)){root.requested.add(data.field.resource_id);readingCommand(root,'request_resource',{resource_id:data.field.resource_id});}return;}
    }
    if(data.field) {
      const before=root.field?.value;const field=readingField(root.scope,data.field);root.field=field;
      if(root.element && before!==field.value && !field.composing) {
        if(data.widget.type==='tabs') root.tabButtons.forEach((b,v)=>b.setAttribute('aria-selected',String(v===field.value)));
        else
        if(data.widget.type==='toggle') root.element.setAttribute('aria-pressed',String(!!field.value));
        else if(data.widget.type==='select') root.element.value=String(Math.max(0,data.widget.options.indexOf(field.value)));
        else root.element.value=field.value??'';
      }
      if(field.conflict) {
        root.notice('Bản trên server đã thay đổi. Nội dung đang nhập vẫn được giữ.');
        field.recovery={value:data.field.value,revision:data.field.revision,replacement:data.field.replacement};
        if(!root.recoveryButtons) {
          const row=document.createElement('div');row.className='reading-recovery';row.style.display='flex';row.style.gap='8px';
          for(const [label,keep] of [['Giữ nội dung đang nhập',true],['Nạp nội dung trên server',false]]) {
            const button=document.createElement('button');button.className='reading-button';button.textContent=label;
            button.addEventListener('click',()=>{
              const f=root.field,r=f.recovery;f.base_revision=r.revision;f.replacement=r.replacement;f.conflict=false;
              if(keep){f.edit_sequence++;f.dirty=true;readingPersist(root.scope,f);readingCommand(root,'checkpoint_draft');}
              else {f.value=r.value;f.dirty=false;root.element.value=r.value;readingPersist(root.scope,f);}
              row.remove();root.recoveryButtons=null;
            },{signal:root.controller.signal});row.append(button);
          }
          root.host.append(row);root.recoveryButtons=row;
        }
      }
    }
    return;
  }
  if(data.type==='display') {
    const value=readingResource(root,data.resource_id,data.resource);
    if(value && root.displayed!==data.resource_id) {
      root.lookupCleanup?.();root.host.replaceChildren();root.lookupCleanup=readingDisplay(root.host,value,root);root.displayed=data.resource_id;
    }
    return;
  }
  if(data.type==='read_workspace') {
    for(const [view,packet] of Object.entries(data.views||{})) {
      const resource=readingResource(root,packet.resource_id,packet.resource);
      if(resource) root.scope.views.set(`${data.instance_role}:${view}`,{resource_id:packet.resource_id,revision:data.view_revisions[view]});
    }
    if(root.pendingView===data.current_view) {root.active=data.current_view;root.pendingView=null;}
    const active=root.scope.views.get(`${data.instance_role}:${root.active}`);
    if(!active || active.revision!==data.view_revisions[root.active]) {
      root.pendingView=root.active;readingCommand(root,'request_view',{choice:root.active});return;
    }
    const resource=root.scope.resources.get(active.resource_id)?.value;
    if(!resource) {readingResource(root,active.resource_id,null);return;}
    root.tabButtons?.forEach((button,view)=>button.setAttribute('aria-selected',String(view===root.active)));
    root.presentations ||= new Map();
    let presentation=root.presentations.get(root.active);
    if(presentation?.resource_id!==active.resource_id) {
      presentation?.cleanup?.();presentation?.node.remove();
      const node=document.createElement('div');root.pane.append(node);
      presentation={resource_id:active.resource_id,node,cleanup:readingDisplay(node,resource,root)};
      root.presentations.set(root.active,presentation);
    }
    for(const [view,p] of root.presentations) p.node.hidden=view!==root.active;
    root.displayed=active.resource_id;
    return;
  }
}
export default function(component) {
  const host=component.parentElement.querySelector('[data-reading-root]'),data=component.data;
  if(!host || data?.schema_version!==1) return;
  if(data.type==='reversible_control') return readingModeControl(component,host,data);
  let root=host.__readingRoot;
  const shape=JSON.stringify([data.type,data.widget,data.tabs]);
  if(root) root.cleanupTicket=null;
  if(root && (root.scope.id!==`${data.ui_session}:${data.document_token}:${data.generation}` || root.shape!==shape)) {root.dispose();root=null;}
  if(!root) {
    const scope=readingScope(data);root={host,data,component,scope,shape,controller:new AbortController(),requested:new Set()};
    root.notice=message=>{let p=host.querySelector('.reading-local-warning');if(!p){p=document.createElement('p');p.className='reading-local-warning';host.append(p);}p.textContent=message;};
    root.dispose=()=>{
      if(root.cleaned) return;root.cleaned=true;root.controller.abort();clearTimeout(root.idleTimer);root.lookupCleanup?.();root.copyBuffer?.remove();
      for(const p of root.presentations?.values()||[]) p.cleanup?.();
      for(const f of scope.fields.values()) readingPersist(scope,f);
      if(scope.roots.get(root.data.instance_role)===root) scope.roots.delete(root.data.instance_role);
      if(!scope.roots.size) {clearTimeout(scope.blurTimer);scope.queue=[];}
      if(host.__readingRoot===root) delete host.__readingRoot;
    };
    root.cleanup=()=>{const ticket={};root.cleanupTicket=ticket;queueMicrotask(()=>{if(root.cleanupTicket===ticket) root.dispose();});};
    host.__readingRoot=root;scope.roots.set(data.instance_role,root);host.replaceChildren();
    try {
      if(data.type==='control' && (!data.field || Object.hasOwn(data.field,'value') || scope.fields.has(data.field.name))) readingBuildControl(root);
      if(data.type==='read_workspace') {
        root.active=data.current_view;root.tabButtons=new Map();
        const tabs=document.createElement('div');tabs.className='reading-tabs';tabs.setAttribute('role','tablist');
        for(const tab of data.tabs) {
          const button=document.createElement('button');button.className='reading-tab';button.setAttribute('role','tab');readingCaption(button,tab.label);
          button.addEventListener('click',()=>{root.active=tab.id;readingUpdate(root,root.data);},{signal:root.controller.signal});tabs.append(button);root.tabButtons.set(tab.id,button);
        }
        root.pane=document.createElement('div');root.pane.setAttribute('role','tabpanel');host.append(tabs,root.pane);
      }
    } catch(_) {root.notice('Không dựng được vùng v2; đang yêu cầu chuyển về giao diện hiện có.');readingCommand(root,'fallback_requested',{reason:'client_setup'});}
  }
  root.component=component;
  try {readingUpdate(root,data);} catch(_) {root.notice('Không dựng được vùng v2; nội dung đang nhập được giữ lại.');readingCommand(root,'fallback_requested',{reason:'client_shape'});}
  return root.cleanup;
}
