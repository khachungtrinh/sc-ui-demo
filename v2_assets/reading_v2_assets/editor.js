/* Local buffers only. The bridge is called by coalesced checkpoints/actions. */
function readingScope(data) {
  const scopes = window.__scappReadingScopes ||= new Map();
  const id = `${data.ui_session}:${data.document_token}:${data.generation}`;
  let scope = scopes.get(id);
  if (!scope) {
    scope = {id, fields:new Map(), fieldProofs:new Map(), roots:new Map(), resources:new Map(), views:new Map(), queue:[], inflight:null, sequence:data.sequence_floor||0, bytes:0, ack:null};
    scopes.set(id,scope);
    // Retain at most the current and one retiring document; no project/secret store.
    while(scopes.size>2) scopes.delete(scopes.keys().next().value);
  }
  return scope;
}
function readingEventId(sequence) {
  const rng=globalThis.crypto;
  if(rng?.randomUUID) return rng.randomUUID();
  if(rng?.getRandomValues){const values=new Uint32Array(4);rng.getRandomValues(values);return 'e'+Array.from(values,v=>v.toString(16).padStart(8,'0')).join('');}
  return `e${Date.now()}_${sequence}_${Math.random().toString(16).slice(2)}`;
}
function readingStorageKey(scope, name) { return `scapp-reading:${scope.id}:${name}`; }
function readingPersist(scope, field) {
  try {
    const key=readingStorageKey(scope,field.name);
    if(field.dirty) sessionStorage.setItem(key,JSON.stringify({value:field.value,edit_sequence:field.edit_sequence,base_revision:field.base_revision,replacement:field.replacement}));
    else sessionStorage.removeItem(key);
  } catch(_) { /* Storage may be unavailable; server checkpoints still work. */ }
}
function readingField(scope, meta) {
  let f=scope.fields.get(meta.name);
  if(!f) {
    f={name:meta.name,value:meta.value,base_revision:meta.revision,edit_sequence:meta.edit_sequence||0,replacement:meta.replacement,dirty:false,composing:false,lastIdle:0};
    try {
      const saved=JSON.parse(sessionStorage.getItem(readingStorageKey(scope,meta.name))||'null');
      if(saved && saved.base_revision===meta.revision && saved.replacement===meta.replacement && typeof saved.value===typeof meta.value) {
        f.value=saved.value;f.edit_sequence=Math.max(f.edit_sequence,saved.edit_sequence);f.dirty=true;
      }
    } catch(_) {}
    scope.fields.set(meta.name,f);
  } else if(meta.replacement!==f.replacement) {
    if(!f.dirty || (scope.ack?.accepted_edit_sequences?.[f.name]||0)>=f.edit_sequence) {
      f.value=meta.value;f.base_revision=meta.revision;f.replacement=meta.replacement;f.dirty=false;
    } else f.conflict=true;
  } else if(!f.dirty && meta.revision>=f.base_revision && Object.hasOwn(meta,'value')) {
    f.value=meta.value;f.base_revision=meta.revision;f.edit_sequence=Math.max(f.edit_sequence,meta.edit_sequence||0);
  }
  if(meta.resource_id && !f.dirty && (Object.hasOwn(meta,'value') || scope.fieldProofs.get(meta.name)===meta.resource_id)) scope.fieldProofs.set(meta.name,meta.resource_id);
  readingPersist(scope,f);return f;
}
function readingAck(scope, ack) {
  if(!ack || ack.ui_session!==scope.id.split(':')[0] || `${ack.ui_session}:${ack.document_token}:${ack.generation}`!==scope.id) return;
  scope.ack=ack;
  for(const [name,seq] of Object.entries(ack.accepted_edit_sequences||{})) {
    const f=scope.fields.get(name);if(!f) continue;
    const revision=ack.revisions?.[name];
    if(revision>=f.base_revision) f.base_revision=revision;
    if(seq>=f.edit_sequence) {f.dirty=false;f.conflict=false;const proof=ack.field_resource_ids?.[name];if(proof) scope.fieldProofs.set(name,proof);}
    readingPersist(scope,f);
  }
  if(scope.inflight?.envelope.event_id===ack.event_id && ['ok','error'].includes(ack.status)) {
    if(ack.status==='error') {
      const owner=scope.roots.get(scope.inflight.envelope.instance_role);
      owner?.notice((ack.messages||[]).join('; '));
    }
    scope.inflight=null;
    readingPump(scope);
  }
}
function readingSnapshots(scope) {
  const snapshots={};
  for(const f of scope.fields.values()) {
    if(f.dirty) snapshots[f.name]={value:f.value,edit_sequence:f.edit_sequence,base_revision:f.base_revision};
  }
  return snapshots;
}
function readingCommand(root,kind,payload={}) {
  const scope=root.scope;
  clearTimeout(scope.blurTimer);
  const signature=JSON.stringify([root.data.instance_role,kind,payload]);
  if(kind==='checkpoint_draft' && !Object.keys(readingSnapshots(scope)).length) return;
  const newer=Object.entries(readingSnapshots(scope)).some(([name,d])=>d.edit_sequence>(scope.inflight?.envelope.drafts?.[name]?.edit_sequence||0));
  if((scope.inflight?.signature===signature && !newer) || scope.queue.some(item=>item.signature===signature)) return;
  scope.queue.push({root,kind,payload,signature});readingPump(scope);
}
function readingPump(scope) {
  if(scope.inflight || !scope.queue.length) return;
  const item=scope.queue.shift(), root=scope.roots.get(item.root.data.instance_role);
  if(!root) return readingPump(scope);
  // Capture on actual send, AFTER any older checkpoint ack rebases the drafts.
  if(Array.from(scope.fields.values()).some(f=>f.composing)) {scope.queue.unshift(item);return;}
  const drafts=readingSnapshots(scope), residents={};
  for(const resource of scope.resources.keys()) residents[resource]=resource;
  for(const resource of scope.fieldProofs.values()) residents[resource]=resource;
  const e={schema_version:1,ui_session:root.data.ui_session,document_token:root.data.document_token,generation:root.data.generation,
    instance_role:root.data.instance_role,event_id:readingEventId(scope.sequence+1),sequence:++scope.sequence,kind:item.kind,
    base_revisions:root.data.base_revisions||{},payload:item.payload,drafts,resident_resources:residents};
  const bytes=new TextEncoder().encode(JSON.stringify(e)).length;
  if(bytes>16*1024*1024) {root.notice('Văn bản vượt giới hạn truyền. Nội dung vẫn ở đây để sao chép; chưa gửi hoặc lưu.');return;}
  scope.inflight={...item,envelope:e};root.component.setTriggerValue('command',e);
}
function readingBindEditor(root, element, field, actionKind) {
  const signal=root.controller.signal;
  const sync=()=>{
    const next=element.type==='checkbox'?element.checked:element.type==='number'?Number(element.value):element.value;
    if(next!==field.value) {field.value=next;field.edit_sequence++;field.dirty=true;readingPersist(root.scope,field);}
  };
  const checkpoint=()=>{
    if(field.composing || !field.dirty) return;
    clearTimeout(root.scope.blurTimer);
    root.scope.blurTimer=setTimeout(()=>readingCommand(root,actionKind||'checkpoint_draft'),60);
  };
  element.addEventListener('compositionstart',()=>{field.composing=true;},{signal});
  element.addEventListener('compositionend',()=>{field.composing=false;sync();readingPump(root.scope);},{signal});
  element.addEventListener('input',()=>{
    sync();clearTimeout(root.idleTimer);
    root.idleTimer=setTimeout(()=>{
      const now=Date.now();if(now-field.lastIdle<15000 || field.composing) return;
      field.lastIdle=now;readingCommand(root,'checkpoint_draft');
    },2000);
  },{signal});
  element.addEventListener('blur',()=>{sync();checkpoint();},{signal});
  element.addEventListener('change',()=>{
    sync();if(element.matches('select,input[type=checkbox],input[type=number]')) {
      // Always send this control snapshot, even if a coalesced ack already stored it.
      field.dirty=true;readingCommand(root,actionKind||'set_document_controls');
    }
  },{signal});
}
function readingStoreResource(scope,id,value) {
  if(!value || scope.resources.has(id)) return;
  const bytes=new TextEncoder().encode(JSON.stringify(value)).length;
  scope.resources.set(id,{value,bytes});scope.bytes+=bytes;
  while(scope.resources.size>8 || scope.bytes>32*1024*1024) {
    const first=scope.resources.keys().next().value;const old=scope.resources.get(first);
    scope.resources.delete(first);scope.bytes-=old.bytes;
  }
}
