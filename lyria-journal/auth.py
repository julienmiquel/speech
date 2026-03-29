import uuid
from http.cookies import SimpleCookie
import streamlit as st

def get_user_id():
    """
    Simulates Google Auth by creating a persistent user ID stored in a cookie.
    Streamlit doesn't natively support setting cookies in the browser without extra libraries.
    We will use a session_state variable as a fallback, and assume an Identity-Aware Proxy
    or similar mechanism sets an X-Goog-Authenticated-User-Email header in a real Cloud Run environment.
    """

    # Check if we are running under IAP (Identity-Aware Proxy) which passes the Google user
    try:
        # Use st.context.headers for Streamlit >= 1.38, fallback if older
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            headers = st.context.headers
        else:
            from streamlit.web.server.websocket_headers import _get_websocket_headers
            headers = _get_websocket_headers()

        iap_user = headers.get("X-Goog-Authenticated-User-Email")
        if iap_user:
            return iap_user.replace("accounts.google.com:", "")
    except Exception:
        pass

    # Fallback to session state (mock auth)
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = f"anon_{str(uuid.uuid4())[:8]}"

    return st.session_state['user_id']
