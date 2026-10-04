"""One application-owned switchboard for the migrated Components v2 islands.

Edit this file, then restart/rerun the application. No environment/session
overrides: each feature uses the same policy. Defaults retain legacy renderers.
These switches do not control pre-existing infrastructure such as pagination.
"""

V2_FEATURES = {
    "ss_content": True,
    "pali_reader": True,
    "dt_full_text": True,
    "dt_snippets": True,
    "ss_table": True,
    "bilingual_reader": True,
    "english_reader": True,
    "dt_results": True,
    "tdk_results": True,
    "sc_offline_default": True,
    "sc_online": True,
    "lcdp_reader": True,
    "pali_json_reader": True,
    "sujato_json_reader": True,
    "search_dictionary": True,
    "aifast_dictionary": True,
    "dictionary_entries": True,
    "dictionary_details": True,
    "chanting_reader": True,
    "sc_offline_dictionary": True,
    "sc_sidebar": True,
    "taisho_reader": True,
    "dpdict_view": True,
    "reading_intake": True,
    "reading_workspace": True,
    "reading_ai_workspace": True,
}
V2_STRICT = False
V2_METRICS = False


def _check_feature(feature):
    if feature not in V2_FEATURES:
        raise KeyError(f"Unknown Components v2 feature: {feature!r}")


def v2_enabled(feature):
    _check_feature(feature)
    return bool(V2_FEATURES[feature])


def v2_strict(feature=None):
    """Surface Python setup errors; eligibility guards still use legacy."""
    if feature is not None:
        _check_feature(feature)
    return bool(V2_STRICT)


def v2_metrics_enabled(feature):
    _check_feature(feature)
    return bool(V2_METRICS)


def record_v2_route(feature, route, **counts):
    """Opt-in, content-free route diagnostics; no session/document history.

    Callers supply fixed reason codes and numeric counts only. This also returns
    a record so controlled validation can collect decisions without log parsing.
    """
    _check_feature(feature)
    allowed = {"text_bytes", "payload_bytes", "pages", "marks", "items"}
    reasons = {"v2", "legacy_disabled", "legacy_text_limit", "legacy_source_text_limit",
               "legacy_payload_limit", "legacy_match_limit", "legacy_page_limit",
               "legacy_page_text_limit", "legacy_invalid_offsets", "legacy_setup_error",
               "legacy_keyword_limit", "legacy_page_size_limit", "legacy_item_limit",
               "legacy_snippet_text_limit", "legacy_snippet_limit", "legacy_extraction_match_limit",
               "legacy_unsupported_shape", "legacy_markdown_shape"}
    record = {"feature": feature, "route": route if route in reasons else "legacy_unsupported_shape"}
    record.update({key: int(value) for key, value in counts.items()
                   if key in allowed and isinstance(value, int)})
    if v2_metrics_enabled(feature):
        import json
        import logging
        logging.getLogger("scapp.components_v2.routes").warning(
            "components_v2_route %s", json.dumps(record, sort_keys=True))
    return record


def record_v2_mount(feature, payload, **counts):
    """Avoid an extra serialization/size scan when diagnostics are disabled."""
    if v2_metrics_enabled(feature):
        import json
        counts['payload_bytes'] = len(json.dumps(payload).encode('utf-8'))
    return record_v2_route(feature, 'v2', **counts)
