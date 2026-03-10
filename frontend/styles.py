import streamlit as st
import base64
import os


def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def apply_modern_theme():
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap');

    :root {
        --primary: #16a34a;
        --primary-dark: #15803d;
        --primary-darker: #166534;
        --primary-light: #22c55e;
        --primary-50: #f0fdf4;
        --primary-100: #dcfce7;
        --primary-200: #bbf7d0;
        --secondary: #0f766e;
        --accent: #f59e0b;
        --accent-light: #fbbf24;
        --bg-main: #f8faf9;
        --bg-card: #ffffff;
        --text-primary: #1a1a2e;
        --text-secondary: #64748b;
        --text-muted: #94a3b8;
        --border: #e2e8f0;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
        --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.04);
        --radius: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
    }

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--bg-main);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }

    h1 { font-size: 2rem; }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.25rem; }

    p, li, span, label, .stMarkdown {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
        line-height: 1.6;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #064e3b 0%, #065f46 30%, #047857 70%, #059669 100%);
        border-right: none;
        box-shadow: 4px 0 15px rgba(0,0,0,0.1);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
        color: white !important;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.2);
        border-color: rgba(255,255,255,0.35);
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .stMetric {
        background: var(--bg-card);
        padding: 1.25rem;
        border-radius: var(--radius);
        border: 1px solid var(--border);
        border-left: 4px solid var(--primary);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }

    .stMetric:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }

    .stMetric [data-testid="stMetricValue"] {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        color: var(--primary-dark);
    }

    .stForm {
        background: var(--bg-card);
        padding: 2rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border);
        box-shadow: var(--shadow-md);
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 1.5px solid var(--border);
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1);
    }

    .stButton > button {
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
    }

    .stButton > button[kind="primary"],
    .stForm .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        box-shadow: 0 4px 14px rgba(22, 163, 74, 0.3);
    }

    .stButton > button[kind="primary"]:hover,
    .stForm .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-darker) 100%);
        box-shadow: 0 6px 20px rgba(22, 163, 74, 0.4);
        transform: translateY(-1px);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--primary-50);
        padding: 4px;
        border-radius: var(--radius);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
    }

    .stDataFrame {
        border-radius: var(--radius);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }

    .stAlert {
        border-radius: var(--radius);
        border: none;
        box-shadow: var(--shadow-sm);
    }

    div[data-testid="stExpander"] {
        border-radius: var(--radius);
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        overflow: hidden;
    }

    .stDivider {
        border-color: var(--border);
    }

    .stPlotlyChart {
        border-radius: var(--radius);
        overflow: hidden;
    }

    @media (max-width: 768px) {
        .stColumns > div {
            min-width: 100% !important;
        }
        h1 { font-size: 1.5rem; }
    }

    .modern-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border);
        box-shadow: var(--shadow-md);
        padding: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
    }

    .modern-card:hover {
        box-shadow: var(--shadow-xl);
        transform: translateY(-4px);
    }

    .hero-section {
        background: linear-gradient(135deg, #064e3b 0%, #047857 50%, #059669 100%);
        border-radius: var(--radius-xl);
        padding: 2.5rem;
        color: white;
        position: relative;
        overflow: hidden;
        margin-bottom: 2rem;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        pointer-events: none;
    }

    .hero-section h1 {
        color: white;
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .hero-section p {
        color: rgba(255,255,255,0.85);
        font-size: 1.05rem;
    }

    .feature-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border);
        box-shadow: var(--shadow-md);
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }

    .feature-card:hover {
        box-shadow: var(--shadow-xl);
        transform: translateY(-6px);
        border-color: var(--primary-200);
    }

    .feature-card img {
        width: 100%;
        height: 160px;
        object-fit: cover;
    }

    .feature-card .card-body {
        padding: 1.25rem;
    }

    .feature-card .card-body h3 {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: var(--text-primary);
    }

    .feature-card .card-body p {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin: 0;
    }

    .stat-card {
        background: var(--bg-card);
        border-radius: var(--radius);
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
        text-align: center;
    }

    .stat-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }

    .stat-card .stat-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .stat-card .stat-value {
        font-family: 'Poppins', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-dark);
        line-height: 1.2;
    }

    .stat-card .stat-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        font-weight: 500;
        margin-top: 0.25rem;
    }

    .social-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        width: 100%;
        padding: 0.7rem 1rem;
        border-radius: 10px;
        border: 1.5px solid var(--border);
        background: var(--bg-card);
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.95rem;
        color: var(--text-primary);
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        margin-bottom: 0.5rem;
    }

    .social-btn:hover {
        background: var(--primary-50);
        border-color: var(--primary-200);
        box-shadow: var(--shadow-sm);
    }

    .social-btn svg {
        width: 20px;
        height: 20px;
    }

    .divider-text {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 1.5rem 0;
        color: var(--text-muted);
        font-size: 0.85rem;
    }

    .divider-text::before,
    .divider-text::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid var(--border);
    }

    .divider-text::before {
        margin-right: 1rem;
    }

    .divider-text::after {
        margin-left: 1rem;
    }

    .login-container {
        max-width: 480px;
        margin: 0 auto;
    }

    .brand-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .brand-header h1 {
        font-family: 'Poppins', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 50%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
    }

    .brand-header p {
        color: var(--text-secondary);
        font-size: 1rem;
    }

    .profile-avatar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        color: white;
        margin: 0 auto 1rem;
        box-shadow: 0 8px 24px rgba(22, 163, 74, 0.3);
    }

    .profile-section {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border);
        box-shadow: var(--shadow-md);
        padding: 2rem;
        margin-bottom: 1.5rem;
    }

    .profile-section h3 {
        font-size: 1.15rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--primary-100);
    }

    .badge-pill {
        display: inline-block;
        background: var(--primary-100);
        color: var(--primary-dark);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.25rem;
    }

    .activity-item {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border);
    }

    .activity-item:last-child {
        border-bottom: none;
    }

    .activity-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--primary);
        margin-top: 0.5rem;
        flex-shrink: 0;
    }

    .sidebar-profile {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }

    .sidebar-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin: 0 auto 0.5rem;
        border: 2px solid rgba(255,255,255,0.3);
    }

    .sidebar-name {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.05rem;
        margin-bottom: 0.15rem;
    }

    .sidebar-role {
        font-size: 0.8rem;
        opacity: 0.75;
        text-transform: capitalize;
    }

    .page-header {
        margin-bottom: 1.5rem;
    }

    .page-header h1 {
        font-size: 1.75rem;
        margin-bottom: 0.25rem;
    }

    .page-header p {
        color: var(--text-secondary);
        font-size: 0.95rem;
    }

    .login-hero-img {
        width: 100%;
        border-radius: var(--radius-xl);
        object-fit: cover;
        max-height: 500px;
        box-shadow: var(--shadow-xl);
    }

</style>
""", unsafe_allow_html=True)
