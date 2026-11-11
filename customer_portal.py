import asyncio
import streamlit as st

from support_workflow import process_complaint

st.set_page_config(page_title="SupportIQ | Customer Care", page_icon="✦", layout="wide")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "support_result" not in st.session_state:
    st.session_state.support_result = None

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#17243a; --muted:#68778d; --blue:#315efb; --mint:#dff8ef; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(145deg,#f7f9ff 0%,#f5fbfa 48%,#f8f9fc 100%); color:var(--ink); }
.block-container { max-width:1180px; padding:2.1rem 2rem 4rem; }
[data-testid="stSidebar"] { background:#101b32; }
[data-testid="stSidebar"] * { color:#edf3ff !important; }
.brand { display:flex; align-items:center; gap:12px; margin-bottom:2rem; }
.brand-mark { width:42px;height:42px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,#5477ff,#38cba5);color:white;font-size:23px;font-weight:800;box-shadow:0 8px 22px #315efb33; }
.brand-name { font:800 1.35rem Manrope,sans-serif; letter-spacing:-.04em; color:#17243a; }
.eyebrow { color:#315efb; text-transform:uppercase; letter-spacing:.13em; font-size:.72rem; font-weight:800; }
.hero-title { font:800 clamp(2rem,4vw,3.2rem)/1.08 Manrope,sans-serif; letter-spacing:-.055em; color:#17243a; margin:.45rem 0 .7rem; }
.hero-copy { color:#68778d; max-width:650px; font-size:1.04rem; line-height:1.65; }
.hero { padding:1rem 0 1.8rem; }
.panel { background:rgba(255,255,255,.88); border:1px solid #e7ebf3; border-radius:22px; padding:1.4rem 1.5rem; box-shadow:0 12px 35px #2032540a; }
.mini-label { color:#68778d; font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; font-weight:700; }
.workflow { display:flex; gap:10px; align-items:center; padding:.72rem 0; border-bottom:1px solid #ffffff20; }
.step { width:27px;height:27px;flex:none;border-radius:9px;background:#ffffff18;display:grid;place-items:center;font-size:.78rem;font-weight:700; }
div[data-testid="stTextArea"] textarea { border-radius:15px; border-color:#dce4f0; background:#fff; }
div.stButton > button[kind="primary"] { background:linear-gradient(100deg,#315efb,#5179ff); border:0; border-radius:12px; min-height:3rem; font-weight:700; box-shadow:0 9px 20px #315efb30; }
div.stButton > button[kind="secondary"] { border-radius:11px; }
[data-testid="stMetric"] { background:#fff; border:1px solid #e7ebf3; border-radius:16px; padding:1rem; }
.stAlert { border-radius:14px; }
@media(max-width:700px){.block-container{padding:1.2rem 1rem 3rem}.panel{padding:1.1rem;border-radius:18px}}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">✦</div><div><div style="font:800 1.2rem Manrope">SupportIQ</div><div style="font-size:.77rem;opacity:.7">Customer care assistant</div></div></div>', unsafe_allow_html=True)
    st.markdown("<div class='mini-label' style='color:#aab9d2'>HOW IT WORKS</div>", unsafe_allow_html=True)
    for n, label in enumerate(["Understand your request", "Find relevant policy", "Prepare a resolution", "Create a support record"], 1):
        st.markdown(f"<div class='workflow'><div class='step'>{n:02}</div><span>{label}</span></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(f"{len(st.session_state.conversation_history)//2} conversations in this session")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.support_result = None
        st.session_state.customer_complaint = ""
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Responses are grounded in the available company policy library. Account and order systems are not queried.")

st.markdown('<div class="hero"><div class="eyebrow">Support, made simpler</div><div class="hero-title">How can we help<br>you today?</div><div class="hero-copy">Tell us what happened. SupportIQ will review your request, look for relevant guidance, and prepare the next best step.</div></div>', unsafe_allow_html=True)

form_col, aside_col = st.columns([1.65, 1], gap="large")
with form_col:
    with st.container(border=True):
        st.markdown("**YOUR MESSAGE**")
        complaint = st.text_area("Describe your issue", height=160, label_visibility="collapsed", placeholder="For example: My order hasn’t arrived yet. Could you help me check what to do?", key="customer_complaint")
        submitted = st.button("✦  Get help", type="primary", use_container_width=True)
with aside_col:
    st.markdown('<div class="panel"><div class="mini-label">What happens next</div><h3 style="margin:.65rem 0 .4rem;font-family:Manrope">A clear path forward</h3><p style="color:#68778d;line-height:1.6">We’ll identify the topic, check available policies, and let you know if a support specialist should review it.</p><div style="background:#eff4ff;border-radius:12px;padding:.8rem;color:#42536f;font-size:.88rem">Please don’t include passwords or payment card details.</div></div>', unsafe_allow_html=True)

if submitted:
    current_complaint = complaint.strip()
    if not current_complaint:
        st.warning("Please describe your issue so we can help.")
    else:
        result = None
        with st.spinner("Reviewing your request and checking the policy library…"):
            try:
                result = asyncio.run(process_complaint(complaint=current_complaint, conversation_history=list(st.session_state.conversation_history)))
            except Exception:
                st.error("We couldn’t process your request right now. Please try again or contact support.")
        if result is not None:
            response = str(result["resolution"].get("customer_response", "No response generated."))
            st.session_state.support_result = result
            st.session_state.conversation_history.extend([{"role":"user","content":current_complaint},{"role":"assistant","content":response}])
            st.rerun()

result = st.session_state.support_result
if result:
    query, knowledge, resolution = result["query_analysis"], result["knowledge_analysis"], result["resolution"]
    st.markdown("### Your support update")
    st.success(resolution.get("customer_response", "No response generated."))
    a, b, c = st.columns(3)
    a.metric("Request type", str(query.get("category") or "other").replace("_", " ").title())
    b.metric("Priority", str(query.get("urgency") or "medium").title())
    c.metric("Sentiment", str(query.get("sentiment") or "neutral").title())
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("#### Support record")
        st.code(result.get("ticket_id", "N/A"), language=None)
        st.caption("Keep this reference if you need to follow up.")
        st.markdown("#### Review status")
        if resolution.get("escalation_required"):
            st.warning("A support specialist should review this request.")
            if resolution.get("escalation_reason"):
                st.write(resolution["escalation_reason"])
        else:
            st.info("No specialist review was flagged for this response.")
    with right:
        st.markdown("#### Policy references")
        sources = resolution.get("policy_sources", [])
        if sources:
            for source in sources:
                st.write(f"📄 {source}")
        else:
            st.caption("No matching policy source was available.")
        st.caption("Policy evidence: " + ("sufficient" if knowledge.get("sufficient_evidence") else "limited"))
    st.caption("SupportIQ provides guidance from available company policies. It does not access live order or account data.")

if st.session_state.conversation_history:
    with st.expander("View conversation", expanded=False):
        for message in st.session_state.conversation_history:
            with st.chat_message(message.get("role", "assistant")):
                st.write(message.get("content", ""))
