# HTML/CSS trích từ DOM đã render

Các cặp `root-NN.html` / `.css` là nội dung Shadow DOM thực của Components v2, lấy từ lần Chromium đã kiểm tra. `INDEX.json` ánh xạ trạng thái, root và biến theme kế thừa.

Đây là trích xuất tĩnh để đọc và đối chiếu khi viết React. Không phải app HTML độc lập: listener JavaScript, Python callbacks, runtime Streamlit, font và CSS kế thừa không tự đi cùng fragment. Đọc JS gốc trong `v2_assets/` hoặc hằng `_JS` trong module Python tương ứng. Khôi phục style ở `:host`/root phù hợp khi chuyển sang React.

Native Streamlit không có HTML template tĩnh của ứng dụng. Đọc `reports/browser/*.dom.json` trường `native`, ảnh cùng tên, source `reference_pages/` và `st_style.py`. DOM/CSS do Streamlit sinh có thể đổi khi đổi phiên bản; không dùng tên class sinh tự động làm contract React.

Một số root sidebar rỗng trước tương tác là hành vi nguyên bản. Ảnh chụp mặc định chưa chứng minh popup/overlay sau hover; xem INTERACTION_CHECKS.json cho hành vi đã được kiểm tra.
