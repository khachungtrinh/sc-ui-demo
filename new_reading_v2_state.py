"""Session-scoped Reading ledger/drafts/resources; deliberately no filesystem I/O."""
from __future__ import annotations
from collections import OrderedDict
import uuid
from new_reading_v2_contracts import CommandError, digest, serialized_bytes, validate_envelope, SECTION_BYTES

STATE_KEY = '_reading_v2'


class ReadingState:
    def __init__(self, session, identity='intake', locked=False):
        self.session = session
        s = session.setdefault(STATE_KEY, {'ui_session': uuid.uuid4().hex, 'generation': 0, 'identity': None})
        if s['identity'] != identity:
            for key in list(session):
                if str(key).startswith('_reading_buffer_') or key in ('_reading_active_view','_reading_translation_tab'):
                    session.pop(key, None)
            s.update(identity=identity, document_token=uuid.uuid4().hex, generation=s['generation'] + 1,
                     native_glossary_cache={}, prepared_index={}, fields={}, roots={}, ledger=OrderedDict(), sequences={}, ack=None, pending=None,
                     executing=None, errors=[], residents={}, resources=OrderedDict(), cache_bytes=0,
                     fallback={}, resource_revisions={}, sidebar_panels={})
        s['locked'] = bool(locked)
        self.s = s

    def metadata(self):
        return {k: self.s[k] for k in ('ui_session', 'document_token', 'generation')}

    def public_key(self, role):
        return 'reading_' + digest([*self.metadata().values(), role])[:24]

    def field(self, name, value, *, state_key=None, editable=True, value_type='text', options=None):
        fields = self.s['fields']
        f = fields.get(name)
        if f is None:
            f = fields[name] = dict(value=value, revision=1, edit_sequence=0, replacement=0)
        elif f['value'] != value:
            f.update(value=value, revision=f['revision'] + 1, replacement=f['replacement'] + 1)
        f.update(state_key=state_key, editable=editable, value_type=value_type, options=options)
        return {'name': name, 'value': value, 'revision': f['revision'], 'edit_sequence': f['edit_sequence'], 'replacement': f['replacement']}

    def field_resource_id(self, name):
        f=self.s['fields'][name]
        return 'field:' + digest([name,f['revision'],f['replacement']])

    def field_transport(self, name):
        f=self.s['fields'][name]
        packet={'name':name, **{k:f[k] for k in ('revision','edit_sequence','replacement')}}
        resource_id=self.field_resource_id(name)
        packet['resource_id']=resource_id
        if not self.s['residents'].get(resource_id): packet['value']=f['value']
        return packet

    def root(self, role, *, kind=None, field=None, disabled=False, source_action=False, options=None):
        if 'seen_roots' in self.s: self.s['seen_roots'].add(role)
        self.s['roots'][role] = dict(kind=kind, field=field, disabled=disabled, source_action=source_action, options=options, required_revisions=tuple(name for name in ({'run_ai_translation':('source','glossary','prompt_config','translation_template_ai'), 'save_prompt_config':('prompt_config',)}.get(kind, ('source',) if kind in ('save_translation','save_ai_template','import_ai_response','run_google_translation','save_source','confirm_restore','load_template') else ())) if name in self.s['resource_revisions']))

    def revise(self, name, value):
        revision = digest(value)
        self.s['resource_revisions'][name] = revision
        return revision

    def ack(self, event, status, message=None, accepted=None):
        ack = {**self.metadata(), 'event_id': event.get('event_id'), 'status': status,
               'accepted_edit_sequences': accepted or {}, 'revisions': {k: f['revision'] for k, f in self.s['fields'].items()},
               'resource_revisions': dict(self.s['resource_revisions']),
               'field_resource_ids': {k:self.field_resource_id(k) for k in self.s['fields']}, 'messages': [message] if message else []}
        self.s['ack'] = ack
        return ack

    def receive(self, raw):
        """Atomically validate snapshots BEFORE touching session fields or queuing actions."""
        event = raw if isinstance(raw, dict) else {}
        try:
            e = validate_envelope(raw)
            if any(e[key] != self.s[key] for key in ('ui_session', 'document_token', 'generation')):
                raise CommandError('stale_document')
            fingerprint = digest(e)
            old = self.s['ledger'].get(e['event_id'])
            if old:
                if old['digest'] != fingerprint:
                    raise CommandError('event_conflict')
                self.s['ack'] = old['ack']
                return old['ack']
            role = e['instance_role']; kind = e['kind']
            root = self.s['roots'].get(role)
            if not root:
                raise CommandError('unregistered_root')
            if kind not in ('checkpoint_draft', 'request_resource', 'fallback_requested') and (root['disabled'] or root['kind'] != kind):
                raise CommandError('action_not_allowed')
            if root['source_action'] and self.s['locked'] and kind not in ('reset_document',):
                raise CommandError('source_locked')
            if e['sequence'] <= self.s['sequences'].get(role, 0):
                raise CommandError('stale_sequence')
            if self.s['pending'] is not None or self.s['executing'] is not None:
                raise CommandError('action_in_progress')
            snapshots = e.get('drafts', {})
            accepted = {}
            for name, d in snapshots.items():
                f = self.s['fields'].get(name)
                if f and self.s['locked'] and f['state_key'] in ('raw_text_editor','process_content_key'):
                    raise CommandError('source_locked')
                if not f or not f['editable'] or not isinstance(d, dict):
                    raise CommandError('draft_field')
                if type(d.get('edit_sequence')) is not int or d['edit_sequence'] < f['edit_sequence']:
                    raise CommandError('stale_edit_sequence')
                if d.get('base_revision') != f['revision']:
                    raise CommandError('stale_field_revision')
                value = d.get('value')
                if f['value_type'] == 'text' and not isinstance(value, str):
                    raise CommandError('text_shape')
                if f['value_type'] == 'boolean' and type(value) is not bool:
                    raise CommandError('boolean_shape')
                if f['value_type'] == 'number' and (type(value) not in (int, float) or not 500 <= value <= 10000 or value % 500):
                    raise CommandError('number_shape')
                if f['options'] is not None and value not in f['options']:
                    raise CommandError('choice')
                accepted[name] = d['edit_sequence']
            # Controls must be bound to this server-owned field/options list.
            if root['field'] and kind in ('set_document_controls', 'load_template', 'process_source'):
                if root['field'] not in snapshots:
                    raise CommandError('missing_control_snapshot')
            payload = e.get('payload', {})
            if set(payload) - {'choice','resource_id','reason','field'}:
                raise CommandError('payload_keys')
            if kind == 'request_resource' and payload.get('resource_id') not in self.s['resources'] and not (root['field'] and payload.get('resource_id')==self.field_resource_id(root['field'])):
                raise CommandError('unknown_resource')
            for required in root.get('required_revisions', ()):
                if e.get('base_revisions', {}).get(required) != self.s['resource_revisions'][required]:
                    raise CommandError('missing_or_stale_resource_revision')
            if root['options'] is not None and payload.get('choice') not in root['options']:
                raise CommandError('action_choice')
            for name, revision in e.get('base_revisions', {}).items():
                if name in root.get('required_revisions', ()) and revision != self.s['resource_revisions'][name]:
                    raise CommandError('stale_resource_revision')
            # All checks succeeded; application drafts are temporary session buffers.
            for name, d in snapshots.items():
                f = self.s['fields'][name]
                if d['edit_sequence'] == f['edit_sequence'] and d['value'] != f['value']:
                    raise CommandError('edit_sequence_conflict')
            for name, d in snapshots.items():
                f = self.s['fields'][name]
                if d['value'] != f['value']:
                    f.update(value=d['value'], revision=f['revision'] + 1)
                f['edit_sequence'] = d['edit_sequence']
                if f['state_key']:
                    self.session[f['state_key']] = d['value']
            self.s['sequences'][role] = e['sequence']
            current_fields = {self.field_resource_id(name) for name in self.s['fields']}
            available = current_fields | set(self.s['resources'])
            for old in list(self.s['residents']):
                if old not in available: self.s['residents'].pop(old,None)
            for name in snapshots:
                # The browser just supplied this exact revision; do not echo its text.
                self.s['residents'][self.field_resource_id(name)] = True
            for resource, stamp in e.get('resident_resources', {}).items():
                if resource in available and stamp == resource:
                    self.s['residents'][resource] = True
            # Historical retries need only fingerprint, accepted sequences and
            # ack. The current payload lives in pending/executing until done.
            record = {'digest': fingerprint, 'accepted': accepted}
            self.s['ledger'][e['event_id']] = record
            while len(self.s['ledger']) > 128:
                self.s['ledger'].popitem(last=False)
            if kind == 'checkpoint_draft':
                record['ack'] = self.ack(e, 'ok', accepted=accepted)
            else:
                self.s['pending'] = e
                record['ack'] = self.ack(e, 'queued', accepted=accepted)
            return record['ack']
        except (CommandError, ValueError, TypeError) as exc:
            # A rejected command never erases browser drafts.
            return self.ack(event, 'error', str(exc))

    def consume(self, role, kind=None):
        event = self.s.get('pending')
        if not event or event['instance_role'] != role or (kind is not None and event['kind'] != kind):
            return None
        self.s['pending'] = None
        self.s['executing'] = event
        record = self.s['ledger'][event['event_id']]
        record['ack'] = self.ack(event, 'executing', accepted=record['accepted'])
        self.s['errors'] = []
        return event

    def end_render(self):
        seen=self.s.get('seen_roots',set(self.s['roots']))
        pending=self.s.get('pending')
        if pending and pending['instance_role'] not in seen:
            self.s['pending']=None
            record=self.s['ledger'][pending['event_id']]
            record['ack']=self.ack(pending,'error','action_unavailable',record['accepted'])
        for role in list(self.s['roots']):
            if role not in seen: self.s['roots'].pop(role,None)

    def fail(self, reason):
        if self.s.get('executing'):
            self.s['errors'].append(str(reason))

    def finish(self):
        e = self.s.get('executing')
        if e:
            record = self.s['ledger'][e['event_id']]
            record['ack'] = self.ack(e, 'error' if self.s['errors'] else 'ok',
                                     '; '.join(self.s['errors']) or None, record['accepted'])
            self.s['executing'] = None
        return self.s['ack']

    def put_resource(self, value):
        key = digest(value)
        size = serialized_bytes(value)
        if size > SECTION_BYTES:
            raise CommandError('section_size')
        cache = self.s['resources']
        if key not in cache:
            cache[key] = {'data': value, 'bytes': size}; self.s['cache_bytes'] += size
        cache.move_to_end(key)
        while len(cache) > 8 or self.s['cache_bytes'] > 32 * 1024 * 1024:
            old_key, old = cache.popitem(last=False)
            self.s['cache_bytes'] -= old['bytes']; self.s['residents'].pop(old_key, None)
        return key

    def transport(self, resource_id, *, force=False):
        cached = self.s['resources'][resource_id]
        return {'resource_id': resource_id, 'resource': cached['data'] if force or not self.s['residents'].get(resource_id) else None}
