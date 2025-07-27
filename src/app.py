import streamlit as st
from datetime import datetime
import re

from agents.extractor_agent import extract_festival_data
from src.firebase_service import save_festival_data

st.set_page_config(
    page_title="FestMap - Telugu Festival Preservation",
    page_icon="🎉",
    layout="wide"
)

if 'festivals' not in st.session_state:
    st.session_state.festivals = []

def show_home_page():
    st.title("🎉 FestMap - Telugu Festival Preservation")

    st.markdown("## 👋 Welcome to **FestMap**")
    st.markdown("""
    FestMap is a community-powered platform to preserve Telugu festivals, rituals, and folklore.  
    🪔 Every detail you submit contributes to safeguarding our heritage with the help of AI.
    """)

    st.markdown("### 🌟 Why Contribute?")
    st.markdown("""
    - 📚 Document regional traditions that might disappear  
    - 🧠 Help train AI to understand local cultural nuances  
    - 🎁 Earn badges and become a **Cultural Champion**  
    """)

    st.markdown("---")

    st.markdown("> _“A culture dies when its stories are forgotten. Help us remember.”_")

    if st.session_state.festivals:
        st.metric("Festivals in this session", len(st.session_state.festivals))

def is_telugu_text(text):
    return bool(re.search(r'[\u0C00-\u0C7F]', text or ""))

def validate_telugu_input(text, field_name, required=True):
    if required and not text.strip():
        st.error(f"{field_name} is required.")
        return False
    if text and not is_telugu_text(text):
        st.error(f"{field_name} must be in Telugu script.")
        return False
    return True

def show_submit_festival_page():
    st.title("🎪 Submit Festival")
    st.markdown("### Please enter all details in *Telugu script only* to maintain cultural authenticity.")

    with st.form("festival_submission_form"):
        festival_name = st.text_input("Festival Name *", placeholder="దసరా, బతుకమ్మ...")
        festival_description = st.text_area("Festival Description *", height=150)
        #state_district = st.text_input("State/District *", placeholder="తెలంగాణ, ఆంధ్రప్రదేశ్...")
        rituals_customs = st.text_area("Rituals/Customs *", height=100)
        #local_name = st.text_input("Local Name (Optional)", placeholder="Other name?")
        #festival_date = st.date_input("Festival Date (Optional)", value=None)
        st.selectbox("Submission Language", options=["Telugu"], index=0, disabled=True)

        submitted = st.form_submit_button("Submit Festival")

        if submitted:
            valid = all([
                validate_telugu_input(festival_name, "Festival Name"),
                validate_telugu_input(festival_description, "Festival Description"),
                validate_telugu_input(rituals_customs, "Rituals/Customs"),
            ])

            if valid:
                with st.spinner("🔍 Verifying festival with local model..."):
                    try:
                        extracted = extract_festival_data(
                            telugu_text=festival_description.strip(),
                            rituals_text=rituals_customs.strip(),
                            expected_festival=festival_name.strip()
                        )

                        for fest in extracted:
                            fest_name = fest.get("festival_name", "other").strip().lower()
                            if fest_name != "other":
                                fest["festival_name"] = festival_name.strip().lower()

                        save_festival_data(extracted)

                        st.session_state.festivals.append({
                            'festival_name': festival_name.strip(),
                            'festival_description': festival_description.strip(),
                            'rituals_customs': rituals_customs.strip(),
                            'submission_date': datetime.now(),
                            'language': 'Telugu'
                        })

                        st.success("🎉 Festival submitted and stored successfully! Thanks for your contribution!")
                        #st.json(extracted)

                    except Exception as e:
                        st.error(f"❌ Error processing festival: {e}")

def show_rewards_page():
    st.title("🎁 Rewards & Badges (coming soon!)")
    st.markdown("Keep contributing and you can earn badges and rewards to show off on your profile!")

    st.header("🏅 Badges You Can Earn")

    col1, col2 = st.columns(2)

    with col1:
        st.image("https://img.icons8.com/color/96/medal.png", width=70)
        st.subheader("First Submission")
        st.write("Submit your very first festival to earn this!")

    with col2:
        st.image("https://img.icons8.com/color/96/trophy.png", width=70)
        st.subheader("10 Festivals Club")
        st.write("You're amazing! Earn this by submitting 10+ festivals.")

    col3, col4 = st.columns(2)

    with col3:
        st.image("https://img.icons8.com/color/96/books.png", width=70)
        st.subheader("Local Folklorist")
        st.write("You're a legend! Earn this by submitting 25+ unique festivals and rituals from your region.")

    with col4:
        st.image("https://img.icons8.com/color/96/crown.png", width=70)
        st.subheader("Cultural Champion")
        st.write("You're a superstar! Earn this by submitting 10+ unique folklore music or dance forms.")

    st.divider()

    st.header("👑 Rewards")
    st.markdown("""
    - Get your name featured on the Leaderboard (Coming soon!!)
    - Earn digital certificates of cultural preservation.
    - Help influence future AI models trained on Telugu heritage. Join our exclusive community of contributors.
    - Access exclusive Festival Contributor Discord (in the future).
    """)

    st.info("These features are coming soon! Start contributing now to unlock them later.")

def main():
    st.sidebar.title("📚 FestMap Navigation")
    page = st.sidebar.radio("Go to:", ["🏠 Home", "📝 Submit Festival", "🎁 Rewards & Badges"])

    if page == "🏠 Home":
        show_home_page()
    elif page == "📝 Submit Festival":
        show_submit_festival_page()
    elif page == "🎁 Rewards & Badges":
        show_rewards_page()

if __name__ == "__main__":
    main()
