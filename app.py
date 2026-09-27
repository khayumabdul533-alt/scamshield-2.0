"""
ScamShield 2.0 - Streamlit web UI
Run with:  streamlit run app.py
Requires scamshield_chain.py in the same folder, and az login already done.
"""

import streamlit as st
from scamshield_chain import analyze_message

st.set_page_config(page_title="ScamShield 2.0", page_icon="🛡️", layout="centered")

RISK_STYLE = {
    "High": {"color": "#D32F2F", "bg": "#FDECEA", "emoji": "🚨"},
    "Medium": {"color": "#B8860B", "bg": "#FFF8E1", "emoji": "⚠️"},
    "Low": {"color": "#2E7D32", "bg": "#E8F5E9", "emoji": "✅"},
}

st.title("🛡️ ScamShield 2.0")
st.caption("Paste a suspicious SMS, WhatsApp, or email message below to check if it's a scam.")

examples = {
    "-- Choose an example --": "",
    "Bank threat scam": "Dear customer, your account will be suspended. Click http://kotak-verify.net/confirm or call 8899001122 immediately to avoid penalty.",
    "Genuine delivery message": "Your order #4521 has been shipped and will arrive tomorrow by 6pm.",
    "Lottery scam": "Congratulations! You have won Rs 25,00,000 in the KBC lucky draw. Share your bank details and OTP to claim your prize now.",
}
choice = st.selectbox("Try an example, or paste your own message below:", list(examples.keys()))

message = st.text_area(
    "Message to analyze",
    value=examples[choice] if choice != "-- Choose an example --" else "",
    height=120,
    placeholder="Paste the SMS, WhatsApp, or email text here...",
)

if st.button("Analyze", type="primary"):
    if not message.strip():
        st.warning("Please enter a message first.")
    else:
        with st.spinner("Running the 5-stage analysis..."):
            try:
                result = analyze_message(message)
            except Exception as e:
                st.error(f"Something went wrong while analyzing: {e}")
                result = None

        if result:
            risk = result.get("risk_level", "Unknown")
            style = RISK_STYLE.get(risk, {"color": "#555", "bg": "#EEE", "emoji": "❓"})

            st.markdown(
                f"""
                <div style="background-color:{style['bg']}; padding:16px; border-radius:10px; border-left:6px solid {style['color']};">
                    <span style="font-size:22px; font-weight:700; color:{style['color']};">
                        {style['emoji']} Risk Level: {risk}
                    </span><br>
                    <span style="color:#333;">Confidence: {result.get('confidence', 'N/A')}</span><br>
                    <span style="color:#333;">{result.get('reason', '')}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.subheader("Why this was flagged")
            evidence = result.get("evidence", [])
            if evidence:
                for point in evidence:
                    st.markdown(f"- {point}")
            else:
                st.markdown("_No suspicious patterns detected._")

            st.subheader("What to do")
            st.info(result.get("recommended_action", ""))

            do_not = result.get("do_not", [])
            if do_not:
                st.markdown("**Avoid:**")
                for item in do_not:
                    st.markdown(f"- {item}")

            with st.expander("See full technical output (entities, patterns, JSON)"):
                st.json(result)

st.divider()
st.caption("ScamShield 2.0 - built with a 5-stage prompt chain (INT112 Prompt Engineering capstone).")
