/* Mount the unchanged accepted dictionary install routine inside a Reading pane. */
function readingDictionary(host, data) {
  const shell=document.createElement('section');shell.dataset.dictionaryRoot='';shell.className='panel-reader-v2 container sujato-reader';
  const style=document.createElement('style');style.textContent=data.css;
  const layout=document.createElement('div');layout.className='dict-layout';
  const left=document.createElement('div');left.className='dict-left';left.style.flexBasis='33%';
  for(const [lang,position] of [['pi',data.pali_position],['en',data.english_position]]) if(position==='left') {
    const panel=document.createElement('aside');panel.dataset.dictPanel=lang;left.append(panel);
  }
  if(left.childElementCount) layout.append(left);
  const content=document.createElement('div');content.className='dict-content text-container';
  content.innerHTML=sanitizeHtml(data.body_html);layout.append(content);
  shell.append(style,layout);shell.style.height=`${data.height}px`;host.append(shell);
  return dictInstall(shell,data);
}
