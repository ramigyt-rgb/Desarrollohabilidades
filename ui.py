import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    :root{
      --bg:#09090B;--panel:#111116;--panel2:#17171E;--text:#F7F7FB;
      --muted:#9B9BA8;--border:rgba(255,255,255,.08);--violet:#D8B4FE;
    }
    .stApp {
      background:
        radial-gradient(circle at 18% 8%, rgba(168,85,247,.12), transparent 30%),
        radial-gradient(circle at 82% 2%, rgba(56,189,248,.08), transparent 28%),
        #09090B;
    }
    [data-testid="stSidebar"]{
      background:rgba(14,14,18,.96);
      border-right:1px solid var(--border);
    }
    [data-testid="stHeader"]{background:rgba(9,9,11,.65);}
    .block-container{max-width:1440px;padding-top:1.6rem;padding-bottom:5rem;}
    h1,h2,h3{letter-spacing:-.035em}
    .hero{
      padding:28px 30px;border:1px solid var(--border);border-radius:28px;
      background:linear-gradient(135deg,rgba(255,255,255,.06),rgba(255,255,255,.018));
      box-shadow:0 24px 70px rgba(0,0,0,.28);margin-bottom:18px;
    }
    .eyebrow{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:#B8B8C5;font-weight:800}
    .hero-title{font-size:2.45rem;font-weight:850;line-height:1.0;margin:.35rem 0 .55rem}
    .hero-sub{color:#AFAFBC;font-size:1rem;max-width:820px}
    .metric-card,.glass{
      border:1px solid var(--border);background:rgba(255,255,255,.035);
      border-radius:22px;padding:18px 19px;height:100%;
    }
    .metric-k{color:#9292A0;font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;font-weight:800}
    .metric-v{font-size:1.8rem;font-weight:850;margin-top:5px}
    .metric-s{color:#A5A5B2;font-size:.78rem;margin-top:3px}
    .module-card{
      border:1px solid var(--border);border-radius:22px;padding:18px 20px;
      background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.02));
      margin-bottom:12px;
    }
    .lesson-pill{
      display:inline-block;border:1px solid rgba(255,255,255,.1);border-radius:999px;
      padding:5px 10px;margin:3px 4px 3px 0;color:#C9C9D3;font-size:.76rem;
    }
    .tiny{color:#8F8F9D;font-size:.77rem}
    .accent-line{height:3px;border-radius:99px;margin:8px 0 15px}
    div[data-testid="stMetric"]{
      border:1px solid var(--border);border-radius:18px;padding:12px 14px;
      background:rgba(255,255,255,.03)
    }
    .stButton>button,.stDownloadButton>button{
      width:100%;border-radius:13px;min-height:44px;font-weight:760;
      border:1px solid rgba(255,255,255,.10);
    }
    .stTextInput input,.stTextArea textarea,.stNumberInput input{
      border-radius:13px!important;
    }
    div[data-baseweb="select"]>div{border-radius:13px!important}
    .stTabs [data-baseweb="tab-list"]{gap:8px}
    .stTabs [data-baseweb="tab"]{
      background:rgba(255,255,255,.035);border:1px solid var(--border);
      border-radius:999px;padding:8px 16px;
    }
    .stProgress > div > div > div > div{border-radius:99px}
    .exam-ok{padding:14px 16px;border-radius:16px;background:rgba(52,211,153,.09);border:1px solid rgba(52,211,153,.18)}
    .exam-bad{padding:14px 16px;border-radius:16px;background:rgba(251,113,133,.08);border:1px solid rgba(251,113,133,.16)}
    footer{visibility:hidden}
    </style>
    """, unsafe_allow_html=True)

def hero(kicker, title, subtitle):
    st.markdown(f"""
    <div class="hero">
      <div class="eyebrow">{kicker}</div>
      <div class="hero-title">{title}</div>
      <div class="hero-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, sub=""):
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-k">{label}</div>
      <div class="metric-v">{value}</div>
      <div class="metric-s">{sub}</div>
    </div>
    """, unsafe_allow_html=True)
