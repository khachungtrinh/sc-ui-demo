"""Reading-scoped public Components v2 adapters; existing page owns all actions.

No global Streamlit monkeypatch. Native exceptions use the original page layout.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
import logging
from pathlib import Path
import streamlit as st
from new_component_v2_support import get_v2_component
from new_components_v2_config import v2_enabled, v2_strict
from new_dictionary_view_v2 import JS as DICTIONARY_JS, dictionary_instance_identity
from new_reading_v2_contracts import EDITOR_BYTES, SECTION_BYTES, CommandError, digest, serialized_bytes
from new_reading_v2_state import ReadingState, STATE_KEY
from new_reading_view_service import cached_presentation, text_resource, table_resource, json_resource
from st_style import STREAMLIT_WIDGET_FONT_SIZE, STREAMLIT_WIDGET_CONTROL_HEIGHT
from new_component_v2_theme import native_dictionary_theme_css
from new_reading_mode_controls import accept_mode_value, mode_store, register_mode

_ASSETS = Path(__file__).parent / 'v2_assets' / 'reading_v2_assets'
JS = (DICTIONARY_JS.split('export default function(component)', 1)[0] + '\n' +
      '\n'.join((_ASSETS / name).read_text(encoding='utf-8') for name in ('editor.js', 'lookup.js', 'modes.js', 'workspace.js')))
CSS = ('[data-reading-root]{--reading-control-size:' + str(STREAMLIT_WIDGET_FONT_SIZE) +
       'px;--reading-control-height:' + str(STREAMLIT_WIDGET_CONTROL_HEIGHT) + 'px;}\n' +
       (_ASSETS / 'reading.css').read_text(encoding='utf-8') + native_dictionary_theme_css())


def _component():
    return get_v2_component('scapp_reading_workspace', '<section data-reading-root></section>', CSS, JS)


def _mount_reversible_control(state, data, key, on_change=None, args=None, kwargs=None):
    """Normal component callback → canonical boolean → normal full-app rerun."""
    if any(data.get(k) != state.s[k] for k in ('ui_session', 'document_token', 'generation')):
        return
    packet = {**data, 'value': bool(state.session[data['state_key']]),
              'confirmed_sequence': mode_store(state)['sequences'].get(data['mode_group'], 0)}

    def receive():
        result = st.session_state.get(key, {})
        event = result.get('mode') if hasattr(result, 'get') else getattr(result, 'mode', None)
        result_code = accept_mode_value(state, event, data, on_change, args, kwargs)
        logging.getLogger('scapp.reading.modes').debug('mode callback role=%s result=%s sequence=%s value=%s',
            data['instance_role'], result_code, event.get('sequence') if isinstance(event, dict) else None,
            event.get('value') if isinstance(event, dict) else None)

    _component()(key=key, data=packet, on_mode_change=receive, height='content')


@st.fragment
def _mount_fragment(state, data, key):
    """Checkpoints rerun only this root. Business commands enter the existing page."""
    if any(data.get(k) != state.s[k] for k in ("ui_session","document_token","generation")):
        return
    packet = {**data, 'ack': state.s.get('ack'), 'base_revisions': dict(state.s['resource_revisions']),
              'sequence_floor': max(state.s['sequences'].values(), default=0)}
    if data.get('field'):
        packet['field'] = state.field_transport(data['field']['name'])
    # Resource requests invalidate only the requested presentation transport proof.
    pending = state.s.get('pending')
    if pending and pending['instance_role'] == data['instance_role'] and pending['kind'] in ('request_resource', 'fallback_requested'):
        event = state.consume(data['instance_role'])
        if event['kind'] == 'request_resource':
            state.s['residents'].pop(event.get('payload', {}).get('resource_id'), None)
        else:
            state.s['fallback'][data['instance_role']] = 'client_setup'
        state.finish(); st.rerun()
    if data.get('resource_id'):
        packet.update(state.transport(data['resource_id']))
    if data.get('views'):
        packet['views'] = {view: state.transport(p['resource_id']) for view, p in data['views'].items()}

    def receive():
        result = st.session_state.get(key, {})
        event = result.get('command') if hasattr(result, 'get') else getattr(result, 'command', None)
        if event:
            state.receive(event)
    _component()(key=key, data=packet, on_command_change=receive, height='content')
    if (state.s.get('pending') or {}).get('instance_role') == data['instance_role']:
        st.rerun()


class _Sidebar:
    def __init__(self, ui):
        self.ui = ui
    def __getattr__(self, name):
        def render(*args, **kwargs):
            with st.sidebar:
                return getattr(self.ui, name)(*args, **kwargs)
        return render


class ReadingUI:
    def __init__(self, session=None, *, identity='intake', locked=False):
        self.session = st.session_state if session is None else session
        self.state = ReadingState(self.session, identity, locked)
        self.state.s["seen_roots"] = set()
        self._mounts = []
        self._mode_callbacks = {}
        self.sidebar = _Sidebar(self)

    def _role(self, widget, label, key=None, v2_role=None):
        return v2_role or ('field_' + str(key) if key else widget + '_' + digest(label)[:18])

    def _reason(self, role, reason):
        self.state.s.setdefault('route_reasons', {})[role] = reason

    def _eligible(self, section, role, value=None):
        if not v2_enabled(section):
            self._reason(role, 'disabled'); return False
        if self.state.s['fallback'].get(role):
            self._reason(role, self.state.s['fallback'][role]); return False
        if isinstance(value, str) and len(value.encode('utf-8')) > EDITOR_BYTES:
            self._reason(role, 'editor_size'); return False
        try:
            _component()
        except Exception:
            if v2_strict(section): raise
            self._reason(role, 'runtime_setup'); return False
        return True

    def _emit(self, role, **body):
        self._reason(role, 'v2')
        data = {**self.state.metadata(), 'schema_version': 1, 'instance_role': role,
                'base_revisions': dict(self.state.s['resource_revisions']), 'sequence_floor': max(self.state.s['sequences'].values(), default=0), **body}
        # Allocate the same public layout position now; mount after page actions
        # so the ack travels on existing roots, without an extra empty UI row.
        slot=st.container(key=self.state.public_key(role)+'_slot')
        self._mounts.append((slot, data, self.state.public_key(role)))

    def _widget(self, typ, label, value=None, *, key=None, buffer_key=None, v2_role=None,
                section='reading_workspace', command_kind=None, on_change=None, on_click=None,
                args=None, kwargs=None, options=None, disabled=False,
                reversible=False, control_group=None, **params):
        if reversible:
            if typ != 'toggle' or command_kind is not None:
                raise ValueError('reversible is restricted to plain boolean mode controls')
            return self._reversible_toggle(label, value, key=key, buffer_key=buffer_key,
                v2_role=v2_role, section=section, on_change=on_change, args=args, kwargs=kwargs,
                disabled=disabled, control_group=control_group, **params)
        role = self._role(typ, label, key, v2_role)
        state_key = buffer_key or key or ('_reading_buffer_' + role)
        choice_widget = typ in ('select', 'tabs')
        if typ not in ('button', 'menu'):
            if disabled and key is None and buffer_key is None:
                self.session[state_key] = value
            elif key == 'raw_text_editor' and role not in self.state.s['fields']:
                self.session[state_key] = value
            self.session.setdefault(state_key, value)
            if choice_widget and self.session[state_key] not in options:
                self.session[state_key] = value
            value = self.session[state_key]
        default_kind = 'set_document_controls' if typ in ('select','tabs','toggle','number','input') else 'checkpoint_draft'
        kind = command_kind or ('set_document_controls' if on_change else default_kind)
        if typ in ('button','menu'):
            kind = command_kind or 'set_document_controls'
        field_name = role if typ not in ('button','menu') else None
        field = self.state.field(field_name, value, state_key=state_key, editable=not disabled,
                value_type='boolean' if typ == 'toggle' else 'number' if typ == 'number' else 'choice' if choice_widget else 'text',
                options=options if choice_widget else None) if field_name else None
        self.state.root(role, kind=kind, field=field_name, disabled=disabled,
                        source_action=kind in ('save_source','confirm_restore','request_restore','process_source'),
                        options=options if typ == 'menu' else None)
        e = self.state.consume(role, kind)
        fired = e is not None
        if fired:
            callback = on_click if typ == 'button' else on_change
            if callback:
                try:
                    callback(*(args or ()), **(kwargs or {}))
                except Exception:
                    self.state.fail('action_failed');self.state.finish();raise
                if typ == 'button':
                    if kind != 'save_source': self.state.finish()
                    st.rerun()
                value = self.session.get(state_key, value)
                field = self.state.field(field_name, value, state_key=state_key, editable=not disabled,
                      value_type='boolean' if typ == 'toggle' else 'number' if typ == 'number' else 'choice' if choice_widget else 'text', options=options if choice_widget else None)
        native_names = {'textarea':'text_area','input':'text_input','select':'selectbox','toggle':'toggle','button':'button','menu':'menu_button','number':'number_input','tabs':'selectbox'}
        if not self._eligible(section, role, value):
            native = getattr(st, native_names[typ])
            native_params = {k:v for k,v in params.items() if k not in ('primary',)}
            native_params['disabled'] = disabled
            if key is not None: native_params['key'] = key
            if on_change: native_params.update(on_change=on_change,args=args,kwargs=kwargs)
            if on_click: native_params.update(on_click=on_click,args=args,kwargs=kwargs)
            if typ in ('button','menu'):
                result = native(label, options, **native_params) if typ=='menu' else native(label, **native_params)
                return e.get('payload',{}).get('choice') if fired and typ=='menu' else True if fired else result
            if typ in ('select', 'tabs'):
                native_params['index']=options.index(value) if value in options and value is not None else None
                result=native(label,[x for x in options if x is not None],**native_params)
            else:
                result=native(label,value=value,**native_params)
            if key is None: self.session[state_key]=result
            return result
        widget = {'type':typ,'label':label,'kind':kind,'disabled':bool(disabled),
                  'options':options,'icon':params.get('icon'), 'primary':params.get('type')=='primary',
                  **{k:v for k,v in params.items() if k in ('height','placeholder','label_visibility','help','min_value','max_value','step')}}
        self._emit(role, type='control', widget=widget, field=field)
        if typ=='button': return fired and on_click is None
        if typ=='menu': return e.get('payload',{}).get('choice') if fired else None
        return self.session.get(state_key, value)

    def text_area(self,label,value='',**kw): return self._widget('textarea',label,value,**kw)
    def text_input(self,label,value='',**kw): return self._widget('input',label,value,**kw)
    def toggle(self,label,value=False,**kw): return self._widget('toggle',label,value,**kw)
    def number_input(self,label,value=0,**kw): return self._widget('number',label,value,**kw)
    def button(self,label,**kw): return self._widget('button',label,**kw)
    def menu_button(self,label,options,**kw): return self._widget('menu',label,options=list(options),**kw)
    def selectbox(self,label,options,index=0,**kw):
        options=list(options); value=options[index] if options and index is not None else None
        if index is None: options=[None]+options
        return self._widget('select',label,value,options=options,**kw)

    def _reversible_toggle(self, label, value=False, *, key=None, buffer_key=None,
                           v2_role=None, section='reading_workspace', on_change=None,
                           args=None, kwargs=None, disabled=False, control_group=None, **params):
        role = self._role('toggle', label, key, v2_role)
        state_key = buffer_key or key or ('_reading_buffer_' + role)
        self.session.setdefault(state_key, value)
        group = control_group or role
        register_mode(self.state, role, state_key, group, disabled)
        if not self._eligible(section, role, self.session[state_key]):
            return st.toggle(label, key=state_key, value=bool(self.session[state_key]),
                disabled=disabled, on_change=on_change, args=args, kwargs=kwargs, **params)
        self._mode_callbacks[role] = (on_change, args, kwargs)
        self._emit(role, type='reversible_control', state_key=state_key, mode_group=group,
                   widget={'type':'toggle', 'label':label, 'disabled':bool(disabled), 'help':params.get('help')})
        return bool(self.session[state_key])

    def inverse_toggles(self,a,b,key_page,label_a,label_b,default_a=False,*,reversible=False):
        from new_component_state_service import get_inverse_toggle_keys, ensure_inverse_toggle_state, sync_inverse_toggle_state
        ka,kb=get_inverse_toggle_keys(key_page)
        ensure_inverse_toggle_state(self.session,ka,kb,default_a)
        pending=self.state.s.get('pending')
        if pending and pending['instance_role'] in ('field_'+ka,'field_'+kb) and pending['kind']=='set_document_controls':
            self.state.consume(pending['instance_role'],'set_document_controls')
            sync_inverse_toggle_state(self.session,ka,kb,'a' if pending['instance_role']=='field_'+ka else 'b')
        with a: av=self.toggle(label_a,key=ka,on_change=lambda:sync_inverse_toggle_state(self.session,ka,kb,'a'),reversible=reversible,control_group=key_page)
        with b: bv=self.toggle(label_b,key=kb,on_change=lambda:sync_inverse_toggle_state(self.session,ka,kb,'b'),reversible=reversible,control_group=key_page)
        return bool(self.session[ka]),bool(self.session[kb])

    def display(self, resource, *, role, section='reading_workspace'):
        self.state.root(role)
        if not self._eligible(section,role): return False
        try:
            resource_id=self.state.put_resource(resource)
            self._emit(role,type='display',**self.state.transport(resource_id));return True
        except (CommandError,TypeError,ValueError):
            self._reason(role,'section_size_or_shape');return False

    def code(self,text,language=None,height=655,**kw):
        if not self.display({'type':'code','value':text,'height':height},role='ai_prompt',section='reading_ai_workspace'):
            st.code(text,language=language,height=height,**kw)
    def json(self,value,expanded=True,**kw):
        if not self.display(json_resource(value,expanded=expanded),role='original_json'):
            st.json(value,expanded=expanded,**kw)
    def table(self,value,height=850,border=False,**kw):
        if not self.display(table_resource(value,height),role='mt_table'):
            st.table(value,height=height,border=border,**kw)


    def _sidebar_panel(self,resource_id,role):
        from new_dictionary_view_v2 import _mount
        data=self.state.s['resources'][resource_id]['data']
        dictionary=data.get('dictionary')
        if dictionary and dictionary['english_position']=='sidebar':
            panel={**dictionary,'role':'panel','panel_language':'en','body_html':'','height':350,'pali_lookup':{},'en_lookup':{}}
            self.state.s['sidebar_panels'][role]=panel
            with st.sidebar:
                _mount(panel, self.state.public_key(role)+'_panel_en')



    def error(self,message,**kw):
        self.state.fail('backend_error');st.error(message,**kw)
    def warning(self,message,**kw):
        if str(message).startswith('Vui lòng dán dữ liệu JSON'): self.state.fail('empty_ai_json')
        st.warning(message,**kw)
    def finish(self):
        self.state.end_render()
        self.state.finish()
        mounts,self._mounts=self._mounts,[]
        for slot,data,key in mounts:
            with slot:
                if data['type'] == 'reversible_control':
                    _mount_reversible_control(self.state,data,key,*self._mode_callbacks[data['instance_role']])
                else:
                    _mount_fragment(self.state,data,key)
    def rerun(self,*args,**kw):
        self.state.finish();st.rerun(*args,**kw)
    def stop(self):
        self.finish();st.stop()
    def switch_page(self,*args,**kw):
        self.state.finish();st.switch_page(*args,**kw)
