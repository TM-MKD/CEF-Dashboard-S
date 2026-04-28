import streamlit as st

st.set_page_config(
    page_title="Login",
    layout="centered",
    initial_sidebar_state="collapsed"
)

ALLOWED_EMAILS = {
    "martin.prickett@mkdons.com",
    "thomas.mitchell@mkdons.com",
    "matty.mortimer@mkdons.com",
}


def enforce_email_login() -> None:
    """Simple email login gate shown at app start."""
    if st.session_state.get("is_authenticated"):
        return

    st.title("Login")
    st.info("Sign in to access the MK Dons Coach Evaluation Framework.")

    email = st.text_input("Email address", placeholder="name@example.com")
    _password = st.text_input("Password", type="password", placeholder="Enter password")

    if st.button("Log in", type="primary"):
        normalized_email = email.strip().lower()

        if not normalized_email or "@" not in normalized_email:
            st.error("Please enter a valid email address.")
            st.stop()

        if normalized_email not in ALLOWED_EMAILS:
            st.error("This email address does not have access.")
            st.stop()

        st.session_state["is_authenticated"] = True
        st.session_state["authenticated_email"] = normalized_email
        st.rerun()

    st.stop()


def render_logout_button() -> None:
    """Small utility to let authenticated users sign out."""
    if not st.session_state.get("is_authenticated"):
        return

    if st.button("🔓 Log out"):
        st.session_state["is_authenticated"] = False
        st.session_state.pop("authenticated_email", None)
        st.rerun()
