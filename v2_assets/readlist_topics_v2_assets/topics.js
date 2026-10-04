export default function(component) {
    const {data,parentElement}=component;
    const root=parentElement.querySelector('[data-readlist-topics-v2]');if(!root||data?.version!==1)return;
    const previous=root.__topics;
    if(previous?.resourceId===data.resource_id){previous.component=component;previous.grid.updateSelection(data.selected||[]);return previous.cleanup;}
    previous?.cleanup();root.replaceChildren();
    const owner={component,resourceId:data.resource_id};
    owner.grid=createSelectionGrid(root,{height:800,label:'Chọn topic',multiple:true,
        columns:[{label:'',exportLabel:'Select',width:25,checkbox:true},{label:'Topics',width:400},{label:'Suttas',width:900}],
        rows:data.rows,selected:data.selected||[]},topics=>owner.component.setStateValue('selection',{revision:owner.component.data.resource_id,topics}));
    owner.cleanup=()=>{owner.grid.dispose();if(root.__topics===owner){root.replaceChildren();delete root.__topics;}};
    root.__topics=owner;return owner.cleanup;
}
