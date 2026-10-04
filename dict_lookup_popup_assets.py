"""Small shared English-popup asset; independent of lookup/data/render modules.

Pāli/IPA placement is intentionally not connected to this contract.
"""
from pathlib import Path

ENGLISH_POPUP_JS = (Path(__file__).resolve().parent / 'v2_assets' / 'r14_assets' / 'english_popup.js').read_text(encoding='utf-8')


def build_english_popup_js() -> str:
    return ENGLISH_POPUP_JS
