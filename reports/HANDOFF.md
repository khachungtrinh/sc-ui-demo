# Handoff — SCAPP UI Reference

- Entrypoint: `app.py`; Python 3.12; `python -m streamlit run app.py` từ root gói.
- Bảy trang; điều khiển `Trạng thái tham chiếu` nằm trong sidebar.
- Style ownership: giữ bốn module gốc; JS/CSS ở `v2_assets/`.
- Dữ liệu: synthetic fixtures; presentation adapters rõ ràng ở `presentation.py`.
- Đọc `UI_COVERAGE_MANIFEST.csv`, `V2_COMPONENT_MANIFEST.json`, `NATIVE_WIDGET_MANIFEST.json`, `DEPENDENCY_MANIFEST.md` và `LIMITATIONS_AND_SUBSTITUTIONS.md`.
- HTML/CSS render thực: `ui_exports/`; ảnh/DOM: `reports/browser/`.
- Không áp dụng như delta production. Đây là app độc lập.
- Chưa có URL public. Bước publish: đưa root gói vào repo riêng, chọn app.py trên Streamlit Community Cloud, Python 3.12, không secrets; mở đủ trang/scenario để xác nhận sau deploy.
- Resume: đọc `WORK_STATE.md`, `WORK_CHECKPOINT.json`, `FAST_RESUME_PROTOCOL.md`. Không lặp lại evidence đã freeze nếu hash khớp.
