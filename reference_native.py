import streamlit as st
import re
from urllib.parse import urlencode


def smarkdown(oj, *, _emit=None):
    (_emit or st.markdown)(oj, unsafe_allow_html=True)


def c_link(name, url) -> str:
    return f'[{name}]({url})'


def reference_links(sutta_id: str, sutta_name: str, dem_tong=0, online_=True, *, p="", _emit=None):
    sutta_name = sutta_id.upper() + ' - ' + str(sutta_name)
    sutta_id = sutta_id.lower()
    url_en = f'https://suttacentral.net/{sutta_id}/en/sujato?lang=en&layout=sidebyside&reference=none&notes=asterisk&highlight=false&script=latin'
    url_vi = f'https://suttacentral.net/{sutta_id}/vi/minh_chau?lang=en&reference=none&highlight=false'
    url_ss = f'/ss?uid={sutta_id}'
    word = str(p or "").strip()
    if word:
        url_ss += "&" + urlencode({"word": word})
    url_rt = f'/td?doc-kinh&uid={sutta_id}' #### ?????
    if online_:
        if dem_tong == 0:
            smarkdown(
            f"<span style='font-size:1.5em; font-weight:bold;'>`{sutta_name}` | </span>"
            f"<sub>"
            f"{c_link('sujato_s', url_en)} - "
            f"{c_link('parallels', url_ss)}"
            # f" - {c_link('readsutta', url_rt)}"
            f"</sub>",
                _emit=_emit,
            )
        else:
            smarkdown(
                f"<span style='font-size:1.5em; font-weight:bold;'>`{sutta_name}` | `x{dem_tong}`</span>"
                f"<sub>"
                f"{c_link('sujato_s', url_en)} - "
                f"{c_link('parallels', url_ss)}"
                # f" - {c_link('readsutta', url_rt)}"
                f"</sub>",
                _emit=_emit,
            )
    else:
        smarkdown(
            f"<span style='font-size:1.5em; font-weight:bold;'>`{sutta_name}` | `x{dem_tong}`</span>"
            f"<sub>"
            f"{c_link('parallels', url_ss)} -"
            f"{c_link('readsutta', url_rt)}"
            f"</sub>",
            _emit=_emit,
        )


def _draw_line_mini(_surface=None):
    ui = _surface if _surface is not None else st
    ui.markdown(
        "<hr style='margin: 0.5em 0; border: 0; border-top: 1px dashed #e0e0e0;'/>",
        unsafe_allow_html=True)


def _format_frequency_label(
    freq_q1,
    freq_q2,
):
    """Return the compact one- or two-keyword frequency label."""
    primary = max(0, int(freq_q1 or 0))
    secondary = max(0, int(freq_q2 or 0))
    if secondary > 0:
        return f"{primary}+{secondary}"
    return str(primary)


def _render_offline_sutta_title(
    sut_id,
    freq_q1,
    freq_q2,
    data_title,
    p="",
    _surface=None,
):
    """
    Giữ cách hiển thị liên kết của code cũ:
    reference_links(..., online_=False).
    """
    ui = _surface if _surface is not None else st
    title_pali = str(
        data_title.get(sut_id, {}).get("title_pali", "") or ""
    ).strip()

    reference_links(
        sut_id,
        title_pali,
        dem_tong=_format_frequency_label(
            freq_q1,
            freq_q2,
        ),
        online_=False,
        p=p,
        _emit=ui.markdown,
    )


def _show_muti_lang(lang1, lang2, lang3, show_col3=False, _surface=None):
    ui = _surface if _surface is not None else st
    if show_col3:
        # Giao diện 3 cột bình thường (Pali - Tiếng Anh - Bản Dịch)
        c_l1, c_l2, c_l3 = ui.columns([1, 1, 1])
        with c_l1:
            smarkdown(lang1, _emit=ui.markdown)
        with c_l2:
            smarkdown(lang2, _emit=ui.markdown)
        with c_l3:
            smarkdown(lang3, _emit=ui.markdown)
    else:
        # Khi more_kq='true', Cột 3 (All contexts) đã được tạo bên ngoài.
        # Nên ở đây ta chỉ cần tạo 2 cột (Pali - Tiếng Anh) cho mỗi kết quả API
        c_l1, c_l2 = ui.columns([1, 1])
        with c_l1:
            smarkdown(lang1, _emit=ui.markdown)
        with c_l2:
            smarkdown(lang2, _emit=ui.markdown)


def _show_sutta_blurb(uid, o_title, data_blurb, p="", _surface=None):
    ui = _surface if _surface is not None else st
    c_l4, c_l5 = ui.columns([2, 3], vertical_alignment="bottom")
    with c_l4:
        reference_links(uid, o_title, p=p, _emit=ui.markdown)

    with c_l5:
        if data_blurb is None:
            pass
        else:
            data_blurb = re.sub(r"</?sub>", "", data_blurb)
            ui.caption(f'{data_blurb}')


def draw_line_dt(opacity="0.65"):
    st.markdown(f"<hr style='margin: 0.5rem 0; opacity: {opacity};'>", unsafe_allow_html=True)
