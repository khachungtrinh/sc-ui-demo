const TAISHO_OVERVIEW='Giới thiệu / Tổng quan';
function taishoResolve(sections, preferred=[]) {
  let filtered=sections, path=[], levels=[];
  const maxDepth=Math.max(0,...sections.map(s=>s.breadcrumb.length));
  for(let depth=0;depth<maxDepth;depth++) {
    const options=[];
    for(const section of filtered) if(section.breadcrumb.length>depth && !options.includes(section.breadcrumb[depth])) options.push(section.breadcrumb[depth]);
    const overview=filtered.find(s=>s.breadcrumb.length===depth);
    if(depth>0 && overview?.overview) options.unshift(TAISHO_OVERVIEW);
    if(!options.length) break;
    const proposed=preferred[depth] ?? (preferred.length===depth && overview?.overview ? TAISHO_OVERVIEW : null);
    const choice=options.includes(proposed)?proposed:options[0]; levels.push({options,choice});
    if(choice===TAISHO_OVERVIEW) break;
    path.push(choice); filtered=filtered.filter(s=>s.breadcrumb.length>depth && s.breadcrumb[depth]===choice);
    if(filtered.length===1 && filtered[0].breadcrumb.length===depth+1) break;
  }
  const index=sections.findIndex(s=>JSON.stringify(s.breadcrumb)===JSON.stringify(path));
  return {path,levels,index};
}
export default function(component) {
  const {data,parentElement}=component;const root=parentElement.querySelector('[data-taisho-root]');
  if(!root || data?.version!==1) return;
  root.__taishoCleanup?.();
  const controller=new AbortController(),signal=controller.signal;
  const identity=data.resource_id+':'+data.revision, storageKey='scapp.taisho.r14:'+identity;
  let preferred=data.initial_path || [];
  try {const saved=JSON.parse(localStorage.getItem(storageKey));if(Array.isArray(saved)&&saved.every(x=>typeof x==='string')) preferred=saved;}catch(_){}
  let current=taishoResolve(data.sections,preferred);
  const on=(el,type,fn)=>el.addEventListener(type,fn,{signal});
  function closeMenus(){root.querySelectorAll('[role=listbox]').forEach(e=>e.hidden=true);root.querySelectorAll('[role=combobox]').forEach(e=>e.setAttribute('aria-expanded','false'));}
  function select(path,publish=true) {
    current=taishoResolve(data.sections,path);
    try{localStorage.setItem(storageKey,JSON.stringify(current.path));}catch(_){}
    draw();
    if(publish) document.dispatchEvent(new CustomEvent('scapp-taisho-r14',{detail:{identity,path:current.path}}));
  }
  function chooser(level,depth) {
    const group=document.createElement('div');group.className='taisho-select';
    const button=document.createElement('button');button.type='button';button.setAttribute('data-scapp-control','button');button.setAttribute('role','combobox');button.setAttribute('aria-expanded','false');button.setAttribute('aria-label',`Tầng ${depth+1}`);
    const label=document.createElement('span');label.className='taisho-label';label.textContent=level.choice;label.title=level.choice;
    const chevron=document.createElement('span');chevron.className='taisho-chevron';chevron.setAttribute('aria-hidden','true');button.append(label,chevron);
    const list=document.createElement('div');list.className='taisho-options';list.setAttribute('role','listbox');list.hidden=true;
    for(const value of level.options){
      const option=document.createElement('button');option.type='button';option.setAttribute('data-scapp-option','');option.setAttribute('role','option');option.setAttribute('aria-selected',String(value===level.choice));option.textContent=value;
      // Per-draw handlers belong to discarded nodes, not document/window.
      option.onclick=()=>{const path=current.path.slice(0,depth);if(value!==TAISHO_OVERVIEW)path.push(value);select(path);root.querySelectorAll('[role=combobox]')[depth]?.focus();};
      option.onkeydown=e=>{if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();(e.key==='ArrowDown'?option.nextElementSibling:option.previousElementSibling)?.focus();}};
      list.append(option);
    }
    button.onclick=()=>{const open=list.hidden;closeMenus();list.hidden=!open;button.setAttribute('aria-expanded',String(open));if(open)list.querySelector('[aria-selected=true]')?.focus();};
    button.onkeydown=e=>{if(e.key==='ArrowDown'){e.preventDefault();button.click();}};
    group.append(button,list);return group;
  }
  function draw() {
    root.replaceChildren();
    if(data.role==='navigation') {
      const nav=document.createElement('div');nav.className='taisho-navigation';
      current.levels.forEach((level,depth)=>nav.append(chooser(level,depth)));
      const buttons=document.createElement('div');buttons.className='taisho-buttons';
      for(const [label,step] of [['Kinh Trước',-1],['Kinh Tiếp',1]]){
        const b=document.createElement('button');b.type='button';b.setAttribute('data-scapp-control','button');b.textContent=label;
        const next=current.index+step;b.disabled=current.index<0||next<0||next>=data.sections.length;
        b.onclick=()=>select(data.sections[next].breadcrumb);buttons.append(b);
      }
      nav.append(buttons);root.append(nav);
    } else {
      root.style.height=`${data.height}px`;
      const body=document.createElement('div');body.className='taisho-content';body.setAttribute('data-scapp-content','');body.tabIndex=0;
      const content=data.sections[current.index]?.content;
      body.textContent=content===undefined?'Không tìm thấy nội dung cho mục này.':content || 'Mục này không có nội dung.';
      if(!content || content.startsWith('[Lỗi'))body.setAttribute('role','alert');
      root.append(body);body.scrollTop=0;
    }
  }
  on(document,'scapp-taisho-r14',e=>{if(e.detail?.identity===identity && Array.isArray(e.detail.path)) select(e.detail.path,false);});
  on(document,'pointerdown',e=>{if(!e.composedPath().includes(root))closeMenus();});
  on(root,'keydown',e=>{if(e.key==='Escape'){closeMenus();root.querySelector('[role=combobox]')?.focus();}});
  draw();const cleanup=()=>controller.abort();root.__taishoCleanup=cleanup;return cleanup;
}
