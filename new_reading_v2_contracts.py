"""Reading-only command boundary. No paths, credentials or executable commands."""
from __future__ import annotations
import hashlib
import json
import re

SCHEMA_VERSION = 1
EDITOR_BYTES = 2 * 1024 * 1024
SECTION_BYTES = 8 * 1024 * 1024
COMMAND_BYTES = 16 * 1024 * 1024
KINDS = frozenset('checkpoint_draft request_view request_resource set_document_controls submit_paste load_sutta process_source save_source request_restore cancel_restore confirm_restore reset_document load_template save_translation run_google_translation refresh_ai_context suggest_ai_context import_ai_response save_ai_template run_ai_translation save_prompt_config save_glossary fallback_requested'.split())
TRANSLATION_FIELDS = frozenset(('draft', 'final'))
TOKEN = re.compile(r'^[A-Za-z0-9_:.-]{1,180}$')
FORBIDDEN = frozenset(('path', 'project_path', 'filename', 'api_key', 'credentials', 'code', 'destination'))


class CommandError(ValueError):
    pass


def serialized_bytes(value):
    return len(json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8'))


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def validate_envelope(raw):
    if not isinstance(raw, dict) or serialized_bytes(raw) > COMMAND_BYTES:
        raise CommandError('command_size_or_shape')
    required = ('schema_version', 'ui_session', 'document_token', 'generation', 'instance_role', 'event_id', 'sequence', 'kind')
    if any(key not in raw for key in required) or raw['schema_version'] != SCHEMA_VERSION:
        raise CommandError('schema')
    for key in ('ui_session', 'document_token', 'instance_role', 'event_id'):
        if not isinstance(raw[key], str) or not TOKEN.fullmatch(raw[key]):
            raise CommandError('identity_shape')
    for key in ('generation', 'sequence'):
        if type(raw[key]) is not int or raw[key] < 1:
            raise CommandError('sequence_shape')
    if raw['kind'] not in KINDS:
        raise CommandError('kind')
    for key in ('payload', 'drafts', 'base_revisions', 'resident_resources'):
        if not isinstance(raw.get(key, {}), dict):
            raise CommandError(key + '_shape')
    if FORBIDDEN.intersection(raw.get('payload', {})):
        raise CommandError('forbidden_payload')
    if 'field' in raw.get('payload', {}) and raw['payload']['field'] not in TRANSLATION_FIELDS:
        raise CommandError('translation_field')
    if len(raw.get('drafts', {})) > 32 or len(raw.get('resident_resources', {})) > 64:
        raise CommandError('snapshot_count')
    return raw
