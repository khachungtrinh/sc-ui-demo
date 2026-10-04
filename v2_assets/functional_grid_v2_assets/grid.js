// Bounded presentational table primitive used only by the two R6 selection frames.
// No provider, random sampling, persistence, Python callback or global event ownership.
function createSelectionGrid(host, options, onSelection) {
    const root=document.createElement('section');root.className='scapp-selection-grid';root.style.height=options.height+'px';host.append(root);
    const scroll=document.createElement('div');scroll.className='grid-scroll';root.append(scroll);
    const table=document.createElement('table');table.setAttribute('data-scapp-dataframe','');table.setAttribute('role','grid');table.setAttribute('aria-label',options.label);
    table.setAttribute('aria-colcount',String(options.columns.length));scroll.append(table);
    const cols=document.createElement('colgroup');const widths=options.columns.map(column=>column.width||null);
    options.columns.forEach((column,index)=>{const col=document.createElement('col');if(widths[index])col.style.width=widths[index]+'px';cols.append(col);});table.append(cols);
    const head=document.createElement('thead'),header=document.createElement('tr');header.setAttribute('role','row');head.append(header);table.append(head);
    const body=document.createElement('tbody');table.append(body);
    if(widths.every(Boolean))table.style.width=widths.reduce((sum,width)=>sum+width,0)+'px';
    const off=[],urls=new Set(),timers=new Set();let disposed=false,selected=new Set(options.selected||[]),query='',sortColumn=null,descending=false,visible=[],focusId=null,focusColumn=0,matches=[],matchIndex=-1;
    const listen=(node,name,fn)=>{node.addEventListener(name,fn);off.push(()=>node.removeEventListener(name,fn));};
    function sync(){for(const row of body.querySelectorAll('tr')){const active=selected.has(row.dataset.rowId);row.setAttribute('aria-selected',String(active));const box=row.querySelector('input');if(box)box.checked=active;}}
    function send(id){if(disposed)return;if(options.multiple){if(selected.has(id))selected.delete(id);else selected.add(id);}else{selected=selected.has(id)?new Set():new Set([id]);}
        sync();onSelection(options.rows.filter(row=>selected.has(row.id)).map(row=>row.id));}
    function focusCell(rowIndex,columnIndex){const rows=body.querySelectorAll('tr');if(!rows.length)return;
        const row=rows[Math.max(0,Math.min(rows.length-1,rowIndex))],cells=row.querySelectorAll('td');focusColumn=Math.max(0,Math.min(cells.length-1,columnIndex));focusId=row.dataset.rowId;
        body.querySelectorAll('td').forEach(cell=>cell.tabIndex=-1);cells[focusColumn].tabIndex=0;cells[focusColumn].focus({preventScroll:true});cells[focusColumn].scrollIntoView({block:'nearest',inline:'nearest'});}
    function updateSearch(){
        const needle=query.toLocaleLowerCase();matches=[];matchIndex=-1;
        body.querySelectorAll('tr').forEach((row,rowIndex)=>row.querySelectorAll('td').forEach((cell,columnIndex)=>{
            const matched=!!needle&&!options.columns[columnIndex].checkbox&&String(visible[rowIndex].values[columnIndex]).toLocaleLowerCase().includes(needle);
            if(matched){cell.setAttribute('data-search-match','');matches.push(cell);}else cell.removeAttribute('data-search-match');
        }));
        if(matches.length){matchIndex=0;matches[0].scrollIntoView({block:'nearest',inline:'nearest'});}
    }
    function draw(){
        visible=[...options.rows];
        if(sortColumn!==null)visible=[...visible].sort((a,b)=>{const left=String(a.values[sortColumn]),right=String(b.values[sortColumn]);return (left<right?-1:left>right?1:0)*(descending?-1:1);});
        body.replaceChildren();table.setAttribute('aria-rowcount',String(visible.length+1));
        visible.forEach((item,index)=>{const row=document.createElement('tr');row.dataset.rowId=item.id;row.setAttribute('role','row');row.setAttribute('aria-rowindex',String(index+2));
            options.columns.forEach((column,columnIndex)=>{const cell=document.createElement('td');cell.dataset.column=String(columnIndex);cell.setAttribute('role','gridcell');cell.setAttribute('aria-colindex',String(columnIndex+1));
                cell.tabIndex=index===0&&columnIndex===0?0:-1;
                if(column.checkbox){cell.setAttribute('data-checkbox-cell','');const box=document.createElement('input');box.type='checkbox';box.setAttribute('type','checkbox');box.tabIndex=-1;box.setAttribute('aria-label','Chọn '+item.values[1]);box.title='Chọn các dòng cần lấy';cell.append(box);}
                else{cell.setAttribute('aria-readonly','true');cell.textContent=String(item.values[columnIndex]);cell.title=String(item.values[columnIndex]);}
                row.append(cell);});body.append(row);});sync();updateSearch();
    }
    options.columns.forEach((column,index)=>{const th=document.createElement('th');th.dataset.column=String(index);th.setAttribute('role','columnheader');th.textContent=column.label;header.append(th);
        if(!column.checkbox){th.tabIndex=0;const sort=()=>{descending=sortColumn===index?!descending:false;sortColumn=index;
            header.querySelectorAll('th').forEach(cell=>cell.removeAttribute('aria-sort'));th.setAttribute('aria-sort',descending?'descending':'ascending');draw();};
            listen(th,'click',event=>{if(!event.target.closest('.grid-resize'))sort();});listen(th,'keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();sort();}});}
        const handle=document.createElement('span');handle.className='grid-resize';handle.setAttribute('aria-hidden','true');th.append(handle);
        let resize=null;listen(handle,'pointerdown',event=>{event.preventDefault();event.stopPropagation();resize={x:event.clientX,width:th.getBoundingClientRect?.().width||widths[index]||150};handle.setPointerCapture?.(event.pointerId);});
        listen(handle,'pointermove',event=>{if(resize){widths[index]=Math.max(column.checkbox?25:40,resize.width+event.clientX-resize.x);cols.children[index].style.width=widths[index]+'px';if(widths.every(Boolean))table.style.width=widths.reduce((sum,width)=>sum+width,0)+'px';}});
        const end=event=>{resize=null;handle.releasePointerCapture?.(event.pointerId);};listen(handle,'pointerup',end);listen(handle,'pointercancel',end);
    });
    listen(body,'click',event=>{const cell=event.target.closest('td'),row=cell?.closest('tr');if(!row)return;focusId=row.dataset.rowId;focusColumn=Number(cell.dataset.column);
        if(!options.multiple||event.target.closest('input[type="checkbox"]'))send(row.dataset.rowId);});
    listen(body,'focusin',event=>{const cell=event.target.closest('td');if(cell){focusId=cell.closest('tr').dataset.rowId;focusColumn=Number(cell.dataset.column);}});
    listen(body,'keydown',event=>{
        const cell=event.target.closest('td');if(!cell)return;const row=cell.closest('tr'),rowIndex=visible.findIndex(item=>item.id===row.dataset.rowId),columnIndex=Number(cell.dataset.column);
        const moves={ArrowDown:[rowIndex+1,columnIndex],ArrowUp:[rowIndex-1,columnIndex],ArrowRight:[rowIndex,columnIndex+1],ArrowLeft:[rowIndex,columnIndex-1],
            Home:[event.ctrlKey?0:rowIndex,0],End:[event.ctrlKey?visible.length-1:rowIndex,options.columns.length-1]};
        if(moves[event.key]){event.preventDefault();event.stopPropagation();focusCell(...moves[event.key]);return;}
        if((event.key===' '||event.key==='Enter')&&(!options.multiple||options.columns[columnIndex].checkbox)){event.preventDefault();event.stopPropagation();send(row.dataset.rowId);return;}
        if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='c'){event.preventDefault();navigator.clipboard?.writeText(String(visible[rowIndex]?.values[columnIndex]??'')).catch?.(()=>{});}
    });
    const tools=document.createElement('div');tools.className='grid-tools';root.append(tools);
    const icons={search:'<circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/>',download:'<path d="M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4"/>',fullscreen:'<path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/>'};
    function tool(kind,label,action){const button=document.createElement('button');button.className='grid-tool';button.type='button';button.dataset.tool=kind;button.setAttribute('aria-label',label);button.title=label;
        button.innerHTML='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">'+icons[kind]+'</svg>';tools.append(button);listen(button,'click',action);return button;}
    const search=document.createElement('input');search.className='grid-search';search.type='search';search.hidden=true;search.setAttribute('aria-label','Tìm kiếm trong bảng');root.append(search);
    tool('search','Tìm kiếm',()=>{search.hidden=!search.hidden;if(!search.hidden)search.focus({preventScroll:true});else{query='';search.value='';updateSearch();}});
    listen(search,'input',()=>{query=search.value;updateSearch();});listen(search,'keydown',event=>{if(event.key==='Escape'){event.preventDefault();search.hidden=true;search.value='';query='';updateSearch();}
        else if(event.key==='Enter'&&matches.length){event.preventDefault();matchIndex=(matchIndex+(event.shiftKey?-1:1)+matches.length)%matches.length;matches[matchIndex].scrollIntoView({block:'nearest',inline:'nearest'});}});
    tool('download','Tải xuống CSV',()=>{const csv=values=>values.map(value=>'"'+String(value).replace(/"/g,'""')+'"').join(',');
        const lines=[csv(options.columns.map(column=>column.exportLabel??column.label)),...options.rows.map(row=>csv(row.values.map((value,index)=>options.columns[index].checkbox?(selected.has(row.id)?'True':'False'):value)))];
        const uri=URL.createObjectURL(new Blob(['\ufeff'+lines.join('\r\n')],{type:'text/csv;charset=utf-8'}));urls.add(uri);
        const link=document.createElement('a');link.href=uri;link.download='data.csv';root.append(link);link.click();link.remove();
        const timer=setTimeout(()=>{timers.delete(timer);if(urls.delete(uri))URL.revokeObjectURL(uri);},0);timers.add(timer);});
    tool('fullscreen','Toàn màn hình',()=>{if(root.ownerDocument?.fullscreenElement===root)root.ownerDocument.exitFullscreen?.();else root.requestFullscreen?.()?.catch?.(()=>{});});
    draw();
    return {root,updateSelection(ids){selected=new Set(ids);sync();},dispose(){if(disposed)return;disposed=true;off.splice(0).forEach(fn=>fn());timers.forEach(clearTimeout);timers.clear();urls.forEach(uri=>URL.revokeObjectURL(uri));urls.clear();root.remove();}};
}
