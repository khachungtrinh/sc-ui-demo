# Dependencies

Runtime: Python 3.12, Streamlit 1.64.0, pandas 2.2.3. Top-level versions are pinned in requirements.txt. Streamlit provides the native React widget frontend and v2 runtime; no Node build is required for deployment. stdlib supplies hashing, JSON, HTML parsing and in-memory state. BeautifulSoup is not required by the selected runtime paths.

Development-only: Playwright 1.58.0 + Chromium 143.0.7499.0 (obtained from @sparticuz/chromium 143.0.4 after standard browser downloads returned invalid ZIPs). Do not install or ship the browser on Community Cloud. Environment capture is separate from minimal deploy requirements; requirements-lock.txt records all 38 resolved runtime distributions for the Python 3.12/Linux validation environment. Use it when matching that environment; Windows wheels/platform dependencies have not been verified.

Excluded: Whoosh/index services, FastAPI/application API client, SQLite/MDX/corpus, DPD DB, Google GenAI/API keys, project persistence, OCR/PDF/media/FFmpeg, YouTube/GitHub downloaders, Anki package storage. Streamlit framework itself retains its ordinary HTTP/WebSocket and session runtime; 'no backend' means no production SCAPP backend.

Original vendored marked-17.0.5.umd.js and its retained source comments/license remain unchanged. Other production assets have byte hashes in REUSE_MANIFEST.json. No CDN fetch is required for selected components.

Official references checked during implementation:
- https://pypi.org/project/streamlit/1.64.0/
- https://docs.streamlit.io/develop/concepts/custom-components/components-v2/theming
- https://docs.streamlit.io/develop/api-reference/configuration/config.toml
