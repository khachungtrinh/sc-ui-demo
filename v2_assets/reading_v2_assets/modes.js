/* Reversible modes use the public state bridge and ordinary app rerun only. */
function readingModeControl(component, host, data) {
  const scopeId = `${data.ui_session}:${data.document_token}:${data.generation}:${data.mode_group}`;
  const groups = window.__scappReadingModeGroups ||= new Map();
  let group = groups.get(scopeId);
  if (!group) { group = {sequence:data.confirmed_sequence || 0, roots:new Map()}; groups.set(scopeId,group); }
  group.sequence = Math.max(group.sequence, data.confirmed_sequence || 0);
  let root = host.__readingMode;
  if (root && root.scopeId !== scopeId) {root.dispose();root=null;}
  if (!root) {
    host.replaceChildren();
    const button = document.createElement('button');button.type='button';button.className='reading-toggle-button';
    readingCaption(button,data.widget.label);button.setAttribute('aria-label',data.widget.label);host.append(button);
    root = {scopeId,host,button,data,component,value:!!data.value,controller:new AbortController()};
    root.paint = value => {root.value=value;button.setAttribute('aria-pressed',String(value));};
    root.dispose = () => {
      root.controller.abort();
      if(group.roots.get(root.data.instance_role)===root) group.roots.delete(root.data.instance_role);
      if(!group.roots.size && groups.get(scopeId)===group) groups.delete(scopeId);
      if(host.__readingMode===root) delete host.__readingMode;
    };
    // Streamlit invokes cleanup before a data update. Retain the live root
    // across that update; dispose listeners on a real unmount.
    root.cleanup = () => {const ticket={};root.cleanupTicket=ticket;queueMicrotask(()=>{if(root.cleanupTicket===ticket) root.dispose();});};
    button.addEventListener('click',()=>{
      if(root.data.widget.disabled) return;
      const value=!root.value;
      for(const sibling of group.roots.values()) sibling.paint(sibling===root ? value : !value);
      root.component.setStateValue('mode', {
        ui_session:root.data.ui_session,document_token:root.data.document_token,generation:root.data.generation,
        instance_role:root.data.instance_role,sequence:++group.sequence,value});
    },{signal:root.controller.signal});
    host.__readingMode=root;group.roots.set(data.instance_role,root);
  }
  root.cleanupTicket=null;root.data=data;root.component=component;
  root.button.disabled=!!data.widget.disabled;root.button.title=data.widget.help || '';
  // An older server render cannot undo a newer click already sent by a sibling.
  if(data.confirmed_sequence >= group.sequence) root.paint(!!data.value);
  else root.paint(root.value);
  host.dataset.rerunOwner='full-app';host.dataset.readingRole=data.instance_role;
  return root.cleanup;
}
