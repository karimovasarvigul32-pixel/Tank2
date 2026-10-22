from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Battle City", page_icon="🛡️", layout="wide")

st.markdown(
    """
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .block-container {padding: 0.5rem 1rem 0 1rem; max-width: 100%;}
    </style>
    """,
    unsafe_allow_html=True,
)

html = (Path(__file__).parent / "index.html").read_text(encoding="utf-8")
components.html(html, height=860, scrolling=False)
st.caption("Boshqaruv: strelkalar / WASD, o'q uzish: Space yoki J. Avval o'yin oynasini bir marta bosing.")
