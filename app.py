import os
import streamlit as st

# Support both the new `google-genai` SDK and legacy `google-generativeai`
try:
    from google import genai
    USE_NEW_GENAI = True
except ImportError:
    try:
        import google.generativeai as genai_legacy
        USE_NEW_GENAI = False
    except ImportError:
        USE_NEW_GENAI = None

# Page configuration
st.set_page_config(
    page_title="AI Article Summarizer",
    page_icon="📰",
    layout="wide"
)

# Custom Styling for polished Hackathon look
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title & Description
st.markdown('<div class="main-header">📰 AI Article Summarizer & Key Points Extractor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">DITE Hackathon 2026-27 | Fast, concise article synthesis powered by Google Gemini</div>', unsafe_allow_html=True)

# Retrieve API Key securely:
# Priority 1: Streamlit secrets
# Priority 2: OS Environment variable
# Priority 3: Sidebar input
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif os.environ.get("GEMINI_API_KEY"):
    api_key = os.environ.get("GEMINI_API_KEY")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    if not api_key:
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Enter your Google Gemini API key here or configure it in secrets/environment variables."
        )
        st.markdown("[Get a Gemini API Key](https://aistudio.google.com/app/apikey)")
    else:
        st.success("API Key detected securely! ✅")

    st.markdown("---")
    st.subheader("💡 About this project")
    st.write(
        "Built for **DITE Hackathon 2026-27** to turn lengthy articles into quick, digestible insights in seconds."
    )
    st.markdown("**Features:**\n- 3-4 sentence concise summary\n- 3 actionable bullet takeaways\n- Secure API key handling")

# Main Input Section
article_text = st.text_area(
    label="Paste your article or long text below:",
    placeholder="Paste news articles, research papers, blog posts, or meeting transcripts here...",
    height=280
)

def generate_summary(text: str, key: str) -> str:
    prompt = f"""
You are an expert AI editor and research assistant.
Analyze the following article and generate:
1. A concise summary in exactly 3 to 4 sentences.
2. Exactly 3 bullet points highlighting the main key takeaways/points.

Format your output strictly using the following Markdown structure:

### 📝 Summary
[Insert 3-4 sentence summary here]

---

### 🔑 Key Takeaways
- [First key point]
- [Second key point]
- [Third key point]

ARTICLE CONTENT:
\"\"\"
{text}
\"\"\"
"""
    if USE_NEW_GENAI:
        client = genai.Client(api_key=key)
        # Try gemini-2.5-flash or gemini-1.5-flash
        for model_name in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception:
                continue
        raise RuntimeError("Could not generate summary with available Gemini models.")
    elif USE_NEW_GENAI is False:
        genai_legacy.configure(api_key=key)
        for model_name in ["gemini-1.5-flash", "gemini-pro"]:
            try:
                model = genai_legacy.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception:
                continue
        raise RuntimeError("Could not generate summary with available Gemini models.")
    else:
        raise ImportError("No Gemini SDK found. Please install google-genai or google-generativeai.")

# Action Button
if st.button("Summarize with AI", type="primary"):
    if not api_key:
        st.error("⚠️ API key is missing! Please configure `GEMINI_API_KEY` in environment variables, Streamlit secrets, or enter it in the sidebar.")
    elif not article_text.strip():
        st.warning("⚠️ Please paste some text before clicking 'Summarize with AI'.")
    elif len(article_text.strip().split()) < 30:
        st.warning("⚠️ The input text is too short. Please provide at least 30-40 words for a meaningful summary.")
    else:
        try:
            with st.spinner("Analyzing text and generating summary with Gemini..."):
                output_text = generate_summary(article_text, api_key)
                st.success("✨ Summary generated successfully!")
                st.markdown(output_text)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
