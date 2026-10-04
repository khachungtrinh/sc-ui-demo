"""Accepted Taisho UI over an already-normalized canonical document response."""
from pathlib import Path
from new_component_v2_support import get_v2_component
from new_components_v2_style import build_components_v2_style_css


def prepare_taisho(document, initial_path=(), height=950):
    # Input is the already-validated, normalized canonical API response.
    return dict(version=document['version'],resource_id=document['resource_id'],revision=document['revision'],
                sections=document['sections'],initial_path=list(initial_path),height=int(height),role='reader')


# Adopt compatible shared metrics only. Legacy colors/focus and unique geometry
# remain local; generic groups would change accepted reader/sidebar surfaces.
_CSS=build_components_v2_style_css('[data-taisho-root]', controls=False, content=False, tables=False) + '\n' + '''
[data-taisho-root]{color:var(--text-color,#3d3a2a);box-sizing:border-box;}
/* Reader typography consumes canonical content metrics through the adapter. */
.taisho-content{height:100%;white-space:pre-wrap;overflow:auto;border:1px solid var(--border-color,#eaeae3);padding:1rem;border-radius:0;box-sizing:border-box;font-family:var(--scapp-v2-font);font-size:var(--scapp-v2-content-font-size);line-height:var(--scapp-v2-content-line-height);}
/* Navigation consumes canonical control metrics; layout remains local. */
.taisho-navigation{width:100%;min-width:0;font-family:var(--scapp-v2-font);font-size:var(--scapp-v2-control-font-size);line-height:var(--scapp-v2-control-line-height);}
.taisho-select{position:relative;margin-bottom:8px;}
.taisho-select>button{width:100%;height:var(--scapp-v2-control-height);display:flex;align-items:center;gap:10px;background:#ecebe3;border:1px solid #d3d2ca;border-radius:0;padding:0 var(--scapp-v2-control-padding-x);color:inherit;font-family:inherit;font-size:inherit;font-weight:400;line-height:var(--scapp-v2-control-line-height);text-align:left;cursor:pointer;box-sizing:border-box;}
.taisho-select>button:hover,.taisho-select>button:focus-visible{border-color:#b8b6ad;outline:none;}
.taisho-label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;min-width:0;}
.taisho-chevron{width:7px;height:7px;border-right:1px solid;border-bottom:1px solid;transform:rotate(45deg);margin-top:-4px;margin-right:4px;flex:none;}
.taisho-options{position:absolute;top:calc(100% + 2px);left:0;right:0;z-index:100;max-height:300px;overflow:auto;background:#fdfdf8;border:1px solid #d3d2ca;box-shadow:0 4px 12px #0002;font-family:inherit;font-size:inherit;}
.taisho-options[hidden]{display:none;}
.taisho-options button{display:block;width:100%;min-height:var(--scapp-v2-control-option-min-height);white-space:normal;overflow-wrap:anywhere;padding:var(--scapp-v2-control-option-padding-y) var(--scapp-v2-control-padding-x);text-align:left;border:0;border-radius:0;background:transparent;color:inherit;font-family:inherit;font-size:inherit;font-weight:400;line-height:var(--scapp-v2-control-line-height);cursor:pointer;}
.taisho-options button:hover,.taisho-options button:focus{background:#ecebe3;outline:none;}
.taisho-options button[aria-selected=true]{background:#ecebe3;font-weight:600;}
.taisho-buttons{display:flex;gap:8px;margin-top:10px;}
.taisho-buttons button{flex:1;height:var(--scapp-v2-control-height);min-width:0;padding:0 8px;border:1px solid #d3d2ca;background:#fdfdf8;color:inherit;border-radius:0;font-family:inherit;font-size:inherit;font-weight:400;line-height:var(--scapp-v2-control-line-height);white-space:nowrap;cursor:pointer;box-sizing:border-box;}
.taisho-buttons button:hover:not(:disabled),.taisho-buttons button:focus-visible:not(:disabled){border-color:#b8b6ad;outline:none;}
.taisho-buttons button:disabled{opacity:var(--scapp-v2-disabled-opacity);cursor:default;}
[data-taisho-root] *{scrollbar-width:thin;scrollbar-color:#ccc transparent;}[data-taisho-root] ::-webkit-scrollbar{width:6px;}[data-taisho-root] ::-webkit-scrollbar-thumb{background:#ccc;}
'''


def render_taisho_v2(document, nav_container, main_container, *, initial_path=(), height=950):
    payload=prepare_taisho(document,initial_path,height)
    js=(Path(__file__).parent/'v2_assets'/'r14_assets'/'taisho.js').read_text(encoding='utf-8')
    render=get_v2_component('scapp_taisho_r14','<section data-taisho-root></section>',_CSS,js)
    # Navigation carries no duplicate content. Both roots share a scoped document event.
    manifest=[{k:s[k] for k in ('breadcrumb','overview')} for s in payload['sections']]
    with nav_container:
        render(data={**payload,'sections':manifest,'role':'navigation'},key='scapp_taisho_r14:nav')
    with main_container:
        render(data=payload,key='scapp_taisho_r14:reader')
