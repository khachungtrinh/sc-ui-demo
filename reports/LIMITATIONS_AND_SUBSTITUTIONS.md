# Báo cáo giới hạn và biện pháp thay thế

## Phạm vi và mức độ nguyên bản

Đã tạo app Streamlit độc lập gồm UI Controls và sáu trang SCAPP, với 39 trạng thái tham chiếu. Đây là bộ renderer và cụm giao diện đại diện phục vụ đọc HTML/CSS/JS khi chuẩn bị React; không phải bản sao toàn bộ mọi nhánh UI của production.

Nguồn là bản sc7.5 đã có R0–R6, hotfix Speaking, gom `v2_assets` và sửa SS/readlist được người dùng xác nhận. Production không được chỉnh sửa. `BASELINE_FILES.json` ghi 260 file nguồn, loại cache Python; số này không dùng để thay thế số file ở các báo cáo gói trước vốn có phạm vi đếm khác.

`REUSE_MANIFEST.json` phân biệt giữ nguyên và trích xuất. Bốn file chủ sở hữu style giữ nguyên byte. Các JS/CSS đã đưa vào `v2_assets` cũng giữ nguyên byte. Các trang reference dùng lại nhãn, tỷ lệ cột và chiều cao của những cụm được chọn; phần điều phối page và lựa chọn scenario là mã mới. Không tuyên bố pixel parity với app production vì chưa chạy app production cùng corpus để đối chiếu ảnh.

## Những phần không giữ nguyên hoàn toàn

| Phần | Giới hạn thực tế | Biện pháp đang dùng / hệ quả |
|---|---|---|
| Dữ liệu production | Không mang corpus, từ điển đầy đủ, project hay dữ liệu riêng vào app public | Fixture tự tạo với tiếng Việt/Pāli/Anh/Hán, ngắn/dài, nhiều hàng và nhiều mục. Độ dài/nội dung làm khác xuống dòng và phân bố cột thực tế. |
| Search/API/DB | Không thực thi Whoosh, FastAPI, SQLite hay gọi dịch vụ SCAPP | Truyền kết quả đã chuẩn bị vào renderer; nút/trường search không phản ánh kết quả tìm kiếm thực. |
| Native Streamlit HTML/CSS | HTML native được frontend của Streamlit sinh lúc chạy, không có template HTML nguồn riêng trong Python | Pin Streamlit; bàn giao native DOM snapshot + ảnh + call sites. Không coi class CSS sinh tự động là contract React. |
| Theme context | Snapshot nguồn không có `.streamlit/config.toml` | Tạo config từ palette khai báo trong `st_style.py`; giữ sáu lời gọi bootstrap. Biến `--st-background-color`, `--st-secondary-background-color`, `--st-text-color` đo được trong v2 là `#fdfdf8`, `#ecebe3`, `#3d3a2a`. Các tùy chọn theme khác của máy production chưa biết. |
| Font/hệ điều hành | Không có font riêng của máy Windows production | Dùng font/fallback của source và Streamlit. Chromium Linux có thể thiếu glyph Hán; không âm thầm thêm font làm đổi typography. |
| Python wrapper phụ thuộc provider | Một số renderer vừa chuẩn bị từ điển vừa mount UI | Tách phần HTML/CSS/JS và hàm chuẩn bị thuần; fixture đi thẳng vào contract trình bày. Không tạo API/repository giả. |
| Hai wrapper cũ | `new_dictionary_entry_v2.FEATURE=dictionary_entry_results` và `new_english_data_reader_v2.FEATURE=english_data_reader` không nằm trong feature config của nguồn này | App reference gọi trực tiếp hàm prepare và component definition gốc. Không sửa feature config production; đây là đường tham chiếu bổ sung, không khẳng định đó là route active trong app chính. |
| SC results | Controller online/offline gắn chặt acquisition/cache | Dùng PreparedPage gốc và trích nguyên các hàm title, multilingual columns, divider; dữ liệu và node selection là fixture. Không tái hiện mọi loại kết quả, nguồn và dictionary mode. |
| SC API/Local controls | Không có internet detection hoặc API thật | Hai toggle hiển thị trạng thái nhưng disabled; chọn nhánh bằng `Trạng thái tham chiếu`. Đây là khác biệt tương tác có chủ đích. |
| SS collection hyperlinks | Nguồn formatter/corpus không đưa vào | Fixture để href trống; menu và table giữ nguyên. Không kiểm chứng hyperlink tới dữ liệu kinh thực. Auto column widths và placeholder height=1000/border=False được giữ. |
| SS readlist | Hàm gốc đọc/lưu tiến độ và chuẩn bị bảng corpus | Wrapper reference giữ bố cục `[1,2,2,1]`, nhãn, callback và table height; thay chuẩn bị bảng bằng fixture. Topic grid dùng assets gốc; không có ghi tiến độ. Nút Nạp bị disabled khi chưa chọn để không đưa lỗi None cũ vào demo. Không sửa lỗi đó trong production. |
| Download/upload | Yêu cầu không thực thi tải/lưu tệp | Uploader bị disabled; download native là nút disabled; nút export CSV của topic grid bị disabled tại wrapper JS reference. Asset file gốc không đổi, nhưng JS ghép khi mount có lớp chặn export. Streamlit `disableDataExport=true` ẩn export native. Clipboard sao chép text ở reader vẫn là hành vi trình bày. |
| Reading project/AI lifecycle | Không được copy cả `page_reading.py` và dependency Gemini/project/filesystem | Trích control/display/state/transport của ReadingUI; dựng cụm intake, read tabs, AI workspace, glossary bằng fixture. Xử lý/lưu/dịch không gọi backend; không tái hiện mọi confirmation/error/project lifecycle. |
| Reading resource tabs | `_english_resource` và `read_workspace` gốc gọi provider/revision | Điều phối fixture dùng contract `read_workspace` và JS gốc; đổi tab và command bridge vẫn chạy trong Streamlit. |
| Tools | Có rất nhiều nhánh liên quan file/media/backend | Chỉ giữ các mẫu UI thật được chọn: readlist edit/create, pills, control rows, tabs, popover xác nhận, ghi chú, expander. Không có filesystem mutation. Một số action chỉ hiển thị phản hồi minh họa. |
| UI Controls | Không phải trang có sẵn trong production | Gallery tham chiếu mới chứa control có trong source. Có multiselect trong DT hiện tại, khác mô tả ban đầu của handoff. Không thêm form khi chưa thấy form trong inventory các trang chính. |
| Media/PDF/Vocab/Anki | Chưa đưa các view phụ này vào các scenario | Không mount WaveSurfer/PDF/Anki/Vocab media, không dùng ảnh giả thay renderer rồi gọi đó là parity. Assets tương ứng không có trong gói. |
| Invisible/global helpers | Scroll/key bridge, sidebar parent-DOM injection, Google Translate injector không phải renderer dữ liệu độc lập | Không copy; giữ sidebar native và phần scroll/pagination cục bộ vốn nằm trong JS của reader. Floating notes/glossary dialog phụ chưa được tái hiện. |
| Browser local storage | Một số assets gốc dùng localStorage/sessionStorage cho UI | Giữ nguyên cho parity trình bày; chỉ chứa dữ liệu minh họa/trạng thái UI, không corpus riêng. Không có persistence server của SCAPP. |
| HTML export | Serialization không chứa listeners, closure JS, các giá trị `.value` chỉ tồn tại dưới dạng DOM property hoặc toàn bộ CSS kế thừa | `ui_exports` dùng để đọc cấu trúc/style, không phải app HTML tương tác độc lập. Dùng cùng JS/fixtures/ảnh và source renderer. |

## Bằng chứng và giới hạn kiểm chứng

- `PYTHON_RUNTIME_CHECKS.json`: 39 trạng thái Python, không exception được ghi nhận.
- `BROWSER_CHECKS.json`: 39 trạng thái Chromium 143 tại 1440×1000; không exception/JS error, không request ngoài origin được quan sát. Component roots có DOM render thực, không chỉ import Python.
- `reports/browser`: ảnh và DOM snapshot cho các trạng thái. `ui_exports` được dẫn xuất từ evidence này, không phải một lần validation lặp lại.
- `INTERACTION_CHECKS.json`: chỉ những tương tác có dòng PASS mới được coi là đã kiểm chứng. Đọc danh sách thực tế; không suy ra mọi popup, keyboard path và edge case đều đã qua.
- Evidence 39 trạng thái là lần chạy trước khi loại bỏ các hàm acquisition/persistence không được gọi; latest Python evidence kiểm tra sau trim. Không sửa HTML/CSS/JS khi trim.
- Chưa kiểm tra pixel-by-pixel với production, Windows, Firefox/Safari, mobile hoàn chỉnh, screen reader, stress/memory/performance hoặc dataset lớn.
- Chưa deploy Community Cloud và chưa có URL public. Cần repository/account đích; README có entrypoint và cấu hình deploy cụ thể.

## Dùng làm đầu vào React

Chuyển từng cụm theo manifest, bắt đầu từ contract fixture và renderer gốc; phân biệt native widget do Streamlit cung cấp với component do SCAPP sở hữu. Khi chuyển một cụm, bổ sung comparison với production thực cho những trạng thái đang thiếu. Chưa viết React và chưa thay đổi backend trong nhiệm vụ này.
