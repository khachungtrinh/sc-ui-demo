"""Small Tier B boolean boundary; independent of editor/transactional commands."""
from __future__ import annotations


def mode_store(state):
    """Initialize only this protocol's metadata for the current document."""
    store = state.s.get('mode_controls')
    if not store or store['document_token'] != state.s['document_token']:
        store = state.s['mode_controls'] = {
            'document_token': state.s['document_token'], 'controls': {}, 'sequences': {}}
    return store


def register_mode(state, role, state_key, group, disabled=False):
    store = mode_store(state)
    store['controls'][role] = {'state_key': state_key, 'group': group, 'disabled': bool(disabled)}
    return store['sequences'].get(group, 0)


def accept_mode_value(state, raw, data, on_change=None, args=None, kwargs=None):
    """Validate the bound public boolean and update canonical state in callback.

    There is no editor snapshot, resource proof, pending/executing action or
    ledger in this protocol. Streamlit owns the ensuing ordinary app rerun.
    """
    if not isinstance(raw, dict) or set(raw) != {
        'ui_session', 'document_token', 'generation', 'instance_role', 'sequence', 'value'}:
        return 'shape'
    if type(raw['generation']) is not int or any(raw[k] != state.s[k] for k in
                                               ('ui_session', 'document_token', 'generation')):
        return 'stale_document'
    role = data['instance_role']
    if raw['instance_role'] != role:
        return 'role'
    store = mode_store(state)
    control = store['controls'].get(role)
    if not control or control['state_key'] != data['state_key'] or control['group'] != data['mode_group']:
        return 'unregistered_control'
    if type(raw['value']) is not bool:
        return 'boolean_shape'
    sequence = raw['sequence']
    if type(sequence) is not int or sequence <= store['sequences'].get(control['group'], 0):
        return 'stale_sequence'
    # Confirm a processed value even when it became disabled in transit. The
    # next public data packet restores canonical paint on both inverse roots.
    store['sequences'][control['group']] = sequence
    if control['disabled'] or (control['state_key'] == 'sidebar_edit_data_key' and state.s['locked']):
        return 'disabled'
    state.session[control['state_key']] = raw['value']
    if on_change:
        on_change(*(args or ()), **(kwargs or {}))
    return 'accepted'
