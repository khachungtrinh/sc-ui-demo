import streamlit as st


# Canonical typography/metrics for custom controls that need to visually match
# Streamlit widgets (e.g. Components v2 controls rendered inside an iframe).
STREAMLIT_WIDGET_FONT_FAMILY = '"Source Sans", "Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
STREAMLIT_WIDGET_FONT_SIZE = 14
STREAMLIT_WIDGET_CONTROL_HEIGHT = 40


def build_scapp_select_control_vars(root_selector: str) -> str:
    """Scoped bridge to native SCAPP/Taisho control chrome for Shadow DOM.

    Colours match config_layout's native palette; radius/padding/line-height
    match the accepted Taisho select. Native popup rendering remains OS-owned.
    """
    root = str(root_selector or "").strip()
    if not root:
        raise ValueError("root_selector must not be empty")
    return f"""{root} {{
    --scapp-control-font: {STREAMLIT_WIDGET_FONT_FAMILY};
    --scapp-control-size: {STREAMLIT_WIDGET_FONT_SIZE}px;
    --scapp-control-height: {STREAMLIT_WIDGET_CONTROL_HEIGHT}px;
    --scapp-control-bg: #ecebe3;
    --scapp-control-text: #3d3a2a;
    --scapp-control-border: #d3d2ca;
    --scapp-control-hover-border: #b5b4ad;
    --scapp-control-radius: 0;
    --scapp-control-padding: 0 12px;
    --scapp-control-line-height: 1.25;
}}"""


def config_layout():
    st.html(
        """
        <style>
        /* =========================================================
           0. KHAI BÁO BIẾN MÀU SẮC (ĐỒNG BỘ VỚI CONFIG.TOML)
        ========================================================= */
        :root {
            --primary-color: #3d3a2a;         /* primaryColor */
            --bg-main: #fdfdf8;               /* backgroundColor */
            --bg-sec: #ecebe3;                /* secondaryBackgroundColor */
            --bg-sidebar: #f0f0ec;            /* theme.sidebar.backgroundColor */
            --text-main: #3d3a2a;             /* textColor */
            --border-main: #d3d2ca;           /* borderColor */

            /* Các màu phát sinh (hiệu ứng hover, text mờ) bạn cũng nên gom vào đây */
            --text-muted: rgba(61, 58, 42, 0.7); 
            --hover-border: #b5b4ad;
            --danger-color: red;
        }

        </style>
        """
    )


def app_layout_style():
    st.html(
        """
        <style>

        /* =========================================================
           SIDEBAR
           ========================================================= */
        section[data-testid="stSidebar"] {
            width: 200px !important;
            min-width: 100px !important;
        }

        section[data-testid="stSidebar"]
        [data-testid="stSidebarContent"] {
            scrollbar-gutter: auto !important;

            padding-left: 0.25rem !important;
            padding-right: 0.25rem !important;
        }


        /* =========================================================
           MAIN CONTENT
           ========================================================= */
        [data-testid="stMainBlockContainer"] {
            padding-left: 0.6rem !important;
            padding-right: 0rem !important;
        
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        
            max-width: 100% !important;
        }


        /* =========================================================
           SIDEBAR NAV
           ========================================================= */
        [data-testid="stSidebarNav"] {
            padding-top: 0 !important;
            margin-top: -70px !important;
        }

        [data-testid="stSidebarNav"] span {
            font-size: 18px !important;
            font-weight: 500 !important;
        }

        [data-testid="stSidebarHeader"] {
            padding-bottom: 0 !important;
        }


        /* =========================================================
           HEADER
           ========================================================= */
        [data-testid="stHeader"] {
            background: transparent !important;
        }
        
        /* =========================================================
           SIDEBAR — GIẢM KHOẢNG CÁCH DỌC GIỮA CÁC ELEMENT
           ========================================================= */
        [data-testid="stSidebar"]
        [data-testid="stSidebarUserContent"]
        [data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }
        
        /* =========================================================
           SIDEBAR SELECTBOX — HIỂN THỊ TÊN DÀI
           ========================================================= */
        
        /* Giá trị đang được chọn */
        section[data-testid="stSidebar"]
        [data-baseweb="select"] {
            font-size: 0.85rem !important;
        }
        
        /* Dropdown menu của selectbox */
        div[role="listbox"] {
            max-width: 520px !important;
        }
        
        /* Mỗi option */
        div[role="option"] {
            font-size: 0.85rem !important;
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
            line-height: 1.25 !important;
            height: auto !important;
            min-height: 2.2rem !important;
            padding-top: 0.4rem !important;
            padding-bottom: 0.4rem !important;
        }

        </style>
        """
    )


def checkbox_as_button_style():
    st.html(
        """
        <style>
        /* =========================================================
           1. CONTAINER
           ========================================================= */
        [data-testid="stElementContainer"]:has([data-testid="stCheckbox"]),
        [data-testid="stCheckbox"] {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            background-color: transparent !important;
        }


        /* =========================================================
           2. ẨN ICON CHECKBOX
           ========================================================= */
        [data-testid="stCheckbox"] label > input + div,
        [data-testid="stCheckbox"] label > div:first-of-type {
            display: none !important;
            width: 0 !important;
            margin: 0 !important;
        }


        /* =========================================================
           3. INNER LABEL STRUCTURE
           ========================================================= */
        [data-testid="stCheckbox"] label > div {
            margin-left: 0 !important;
            padding-left: 0 !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
        }


        /* =========================================================
           4. BUTTON-LIKE LABEL
           ========================================================= */
        [data-testid="stCheckbox"] label {
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;

            width: 100% !important;

            margin: 0 !important;
            gap: 0 !important;

            padding: 0.45rem 0.75rem !important;

            border: 1px solid var(--border-main) !important;
            border-radius: 2px !important;

            box-sizing: border-box !important;

            cursor: pointer !important;

            transition:
                background-color 0.2s ease,
                border-color 0.2s ease,
                color 0.2s ease !important;
        }


        /* =========================================================
           5. BACKGROUND THEO VỊ TRÍ
           ========================================================= */
        [data-testid="stSidebar"]
        [data-testid="stCheckbox"] label {
            background-color: var(--bg-sidebar) !important;
        }

        [data-testid="stMain"]
        [data-testid="stCheckbox"] label,
        section:not([data-testid="stSidebar"])
        [data-testid="stCheckbox"] label {
            background-color: var(--bg-main) !important;
        }


        /* =========================================================
           6. TYPOGRAPHY
           Không quản lý font-size ở đây.
           ========================================================= */
        [data-testid="stCheckbox"] label p {
            font-family: inherit !important;
            font-weight: 400 !important;

            color: var(--text-muted) !important;

            margin: 0 !important;
            text-align: left !important;
            width: 100% !important;
        }


        /* =========================================================
           7. HOVER
           ========================================================= */
        [data-testid="stCheckbox"] label:hover {
            background-color: var(--bg-sec) !important;
            border-color: var(--hover-border) !important;
        }


        /* =========================================================
           8. CHECKED
           ========================================================= */
        [data-testid="stCheckbox"]:has(input:checked) label {
            background-color: var(--bg-sec) !important;

            border: 1px solid var(--border-main) !important;

            box-shadow:
                0 1px 3px rgba(0, 0, 0, 0.05) !important;
        }

        [data-testid="stCheckbox"]:has(input:checked) label p {
            color: var(--text-main) !important;
            font-weight: 500 !important;
        }
        </style>
        """
    )


def sidebar_widget_font_size(size=STREAMLIT_WIDGET_FONT_SIZE):
    st.html(
        f"""
        <style>
        /* =========================================================
           WIDGET LABEL
           ========================================================= */
        [data-testid="stSidebar"]
        [data-testid="stWidgetLabel"] p {{
            font-size: {size}px !important;
        }}


        /* =========================================================
           TEXT INPUT
           ========================================================= */
        [data-testid="stSidebar"]
        [data-testid="stTextInput"] input {{
            font-size: {size}px !important;
        }}


        /* =========================================================
           TEXT AREA
           ========================================================= */
        [data-testid="stSidebar"]
        [data-testid="stTextArea"] textarea {{
            font-size: {size}px !important;
        }}


        /* =========================================================
           SELECTBOX
           ========================================================= */
        [data-testid="stSidebar"]
        [data-testid="stSelectbox"] input,

        [data-testid="stSidebar"]
        [data-testid="stSelectbox"] button,

        [data-testid="stSidebar"]
        [data-testid="stSelectbox"] span {{
            font-size: {size}px !important;
        }}


        /* =========================================================
           MULTISELECT
           ========================================================= */
        [data-testid="stSidebar"]
        [data-testid="stMultiSelect"] input,

        [data-testid="stSidebar"]
        [data-testid="stMultiSelect"] button,

        [data-testid="stSidebar"]
        [data-testid="stMultiSelect"] span {{
            font-size: {size}px !important;
        }}


        /* =========================================================
           CHECKBOX
           ========================================================= */
        [data-testid="stSidebar"]
        [data-testid="stCheckbox"] label p,

        [data-testid="stSidebar"]
        [data-testid="stCheckbox"] label span {{
            font-size: {size}px !important;
        }}
        </style>
        """
    )


def sidebar_collapse_style():
    st.html(
        """
        <style>
            [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] { display: none !important; }
        </style>
        """
    )


def main_page_style():
    st.html(
        """
        <style>
            .block-container {
            margin-top: 5px !important;      
            }
            [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stMainMenu"], footer {visibility: hidden !important; }
        </style>
        """
    )
