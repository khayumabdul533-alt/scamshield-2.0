"""
ScamShield 2.0 - Streamlit web UI
Run with:  streamlit run app.py
Requires scamshield_chain.py in the same folder, and az login already done.
"""

import streamlit as st
from scamshield_chain import analyze_message
from file_reader import extract_text_from_file

st.set_page_config(page_title="ScamShield 2.0", page_icon="\U0001F6E1", layout="centered")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .ss-header { display: flex; align-items: center; gap: 14px; margin-bottom: 2px; }
    .ss-header .ss-icon { font-size: 34px; line-height: 1; }
    .ss-header .ss-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700; font-size: 34px; color: #10233A; letter-spacing: -0.5px;
    }
    .ss-tagline { color: #52657A; font-size: 15px; margin: 4px 0 26px 0; }

    .ss-chip-label { font-size: 13px; color: #52657A; margin-bottom: 6px; }

    div.stButton > button {
        border-radius: 8px; font-weight: 500; border: 1px solid #DCE3E8;
    }
    div.stButton > button[kind="primary"] {
        background-color: #1C6E8C; border: none; font-weight: 600;
    }
    div.stButton > button[kind="primary"]:hover { background-color: #175A72; }

    .ss-panel {
        border: 1px solid #DCE3E8; border-radius: 10px; padding: 20px 22px;
        background-color: #FFFFFF; margin-top: 18px;
    }
    .ss-verdict-label {
        font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 21px;
    }
    .ss-reason { color: #33465C; font-size: 14.5px; margin-top: 6px; }
    .ss-confidence { color: #52657A; font-size: 13px; margin-top: 4px; }

    .ss-scale-track {
        position: relative; height: 10px; border-radius: 6px; margin: 18px 0 10px 0;
        background: linear-gradient(to right, #2F7D5B 0%, #2F7D5B 33%, #B8860B 33%, #B8860B 66%, #B23A2E 66%, #B23A2E 100%);
        opacity: 0.35;
    }
    .ss-scale-marker {
        position: absolute; top: -7px; width: 0; height: 0;
        border-left: 9px solid transparent; border-right: 9px solid transparent;
        transform: translateX(-50%);
    }
    .ss-scale-labels { display: flex; justify-content: space-between; font-size: 12px; color: #7A8A9A; margin-bottom: 4px; }

    .ss-section-title { font-weight: 600; color: #10233A; margin-top: 22px; margin-bottom: 8px; font-size: 15px; }
    .ss-evidence-item { padding: 7px 0; border-bottom: 1px solid #EEF1F4; color: #33465C; font-size: 14.5px; }
    .ss-avoid-item { color: #B23A2E; font-size: 14px; padding: 3px 0; }

    footer, #MainMenu { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

RISK_META = {
    "High":   {"color": "#B23A2E", "position": 83.5, "emoji": "\u26D4"},
    "Medium": {"color": "#B8860B", "position": 50.0, "emoji": "\u26A0\uFE0F"},
    "Low":    {"color": "#2F7D5B", "position": 16.5, "emoji": "\u2705"},
}

EXAMPLES = {
    "Bank threat scam": "Dear customer, your account will be suspended. Click http://kotak-verify.net/confirm or call 8899001122 immediately to avoid penalty.",
    "Genuine delivery message": "Your order #4521 has been shipped and will arrive tomorrow by 6pm.",
    "Lottery scam": "Congratulations! You have won Rs 25,00,000 in the KBC lucky draw. Share your bank details and OTP to claim your prize now.",
}

if "message_text" not in st.session_state:
    st.session_state.message_text = ""

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="ss-header">
        <div class="ss-icon">&#128737;&#65039;</div>
        <div class="ss-title">ScamShield 2.0</div>
    </div>
    <div class="ss-tagline">Paste a suspicious SMS, WhatsApp, or email message to check whether it's a scam.</div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Example chips - loads text only when clicked, never automatically
# ---------------------------------------------------------------------------
st.markdown('<div class="ss-chip-label">Try an example:</div>', unsafe_allow_html=True)
cols = st.columns(len(EXAMPLES))
for col, (label, text) in zip(cols, EXAMPLES.items()):
    if col.button(label, use_container_width=True):
        st.session_state.message_text = text
        st.rerun()

message = st.text_area(
    "Message to analyze",
    key="message_text",
    height=120,
    placeholder="Paste the SMS, WhatsApp, or email text here...",
    label_visibility="collapsed",
)

uploaded_file = st.file_uploader(
    "Or upload a screenshot, photo, or file",
    type=["png", "jpg", "jpeg", "webp", "pdf", "txt"],
)

analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
if analyze_clicked:
    text_to_analyze = message.strip()
    if uploaded_file is not None:
        extracted = ""
        with st.spinner("Reading your file..."):
            try:
                extracted = extract_text_from_file(
                    uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or ""
                )
            except Exception as e:
                st.error(f"Could not read the file: {e}")
        if extracted == "NO_MESSAGE_FOUND":
            st.warning("No readable message was found in that file.")
        elif extracted:
            text_to_analyze = (text_to_analyze + "\n\n" + extracted).strip()
            with st.expander("What ScamShield read from your file"):
                st.text(extracted)

    if not text_to_analyze:
        st.warning("Please enter a message or upload a file first.")
    else:
        with st.spinner("Running the 5-stage analysis..."):
            try:
                result = analyze_message(text_to_analyze)
            except Exception as e:
                st.error(f"Something went wrong while analyzing: {e}")
                result = None

        if result:
            risk = result.get("risk_level", "Medium")
            meta = RISK_META.get(risk, RISK_META["Medium"])

            st.markdown('<div class="ss-panel">', unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="ss-verdict-label" style="color:{meta['color']};">{meta['emoji']} {risk} risk</div>
                <div class="ss-confidence">Confidence: {result.get('confidence', 'N/A')}</div>
                <div class="ss-reason">{result.get('reason', '')}</div>

                <div class="ss-scale-labels"><span>Low</span><span>Medium</span><span>High</span></div>
                <div class="ss-scale-track">
                    <div class="ss-scale-marker" style="left:{meta['position']}%; border-top: 12px solid {meta['color']};"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            evidence = result.get("evidence", [])
            st.markdown('<div class="ss-section-title">Why this was flagged</div>', unsafe_allow_html=True)
            if evidence:
                for point in evidence:
                    st.markdown(f'<div class="ss-evidence-item">{point}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ss-evidence-item">No suspicious patterns detected.</div>', unsafe_allow_html=True)

            st.markdown('<div class="ss-section-title">What to do</div>', unsafe_allow_html=True)
            st.info(result.get("recommended_action", ""))

            do_not = result.get("do_not", [])
            if do_not:
                st.markdown('<div class="ss-section-title">Avoid</div>', unsafe_allow_html=True)
                for item in do_not:
                    st.markdown(f'<div class="ss-avoid-item">&#10005; {item}</div>', unsafe_allow_html=True)

            with st.expander("See full technical output (entities, patterns, JSON)"):
                st.json(result)

st.markdown(
    '<div style="color:#9AA8B5; font-size:12.5px; margin-top:40px;">'
    "ScamShield 2.0 &mdash; built with a 5-stage prompt chain (INT112 Prompt Engineering capstone)."
    "</div>",
    unsafe_allow_html=True,
)
