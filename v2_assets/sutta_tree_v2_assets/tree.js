export default function(component) {
    const {data,parentElement}=component;
    const root=parentElement.querySelector('[data-sutta-tree-v2]');
    if(!root||data?.version!==1)return;
    const previous=root.__tree;
    if(previous?.resourceId===data.resource_id){previous.component=component;return previous.cleanup;}
    const focusLevel=previous?.focusLevel;previous?.cleanup();root.replaceChildren();
    const owner={component,resourceId:data.resource_id,focusLevel};
    for(const level of data.levels){
        const select=document.createElement('select');select.setAttribute('data-scapp-control','select');
        select.dataset.level=String(level.level);select.setAttribute('aria-label','Cấp '+(level.level+1));
        for(const value of level.options){const option=document.createElement('option');option.value=value;option.textContent=value;select.append(option);}
        select.value=level.selected;root.append(select);
    }
    const change=event=>{
        const select=event.target.closest('select[data-level]');if(!select||!root.contains(select))return;
        const level=Number(select.dataset.level),entry=owner.component.data.levels[level];
        if(!entry||!entry.options.includes(select.value)||entry.selected===select.value)return;
        owner.focusLevel=level;
        owner.component.setStateValue('selection',{revision:owner.component.data.resource_id,level,value:select.value});
    };
    const focus=event=>{const select=event.target.closest('select[data-level]');if(select)owner.focusLevel=Number(select.dataset.level);};
    root.addEventListener('change',change);root.addEventListener('focusin',focus);
    owner.cleanup=()=>{root.removeEventListener('change',change);root.removeEventListener('focusin',focus);if(root.__tree===owner){root.replaceChildren();delete root.__tree;}};
    root.__tree=owner;
    if(Number.isInteger(focusLevel))root.querySelectorAll('select')[focusLevel]?.focus({preventScroll:true});
    return owner.cleanup;
}
