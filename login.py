import streamlit as st
import hashlib
from database import get_connection

def check_credentials(email, password):
    hash_password = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_utilisateur, nom, prenom, role
        FROM utilisateurs
        WHERE email = %s AND mot_de_passe = %s
    """, (email, hash_password))
    result = cur.fetchone()
    conn.close()
    return result

def login_page():
    st.markdown("""
    <div class="header">
        <h1>Connexion - ERP ESCOA</h1>
        <p>Veuillez vous authentifier pour continuer</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter")

        if submit:
            user = check_credentials(email, password)
            if user:
                id_utilisateur, nom, prenom, role = user
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = id_utilisateur
                st.session_state["user_nom"] = nom
                st.session_state["user_prenom"] = prenom
                st.session_state["user_email"] = email
                st.session_state["user_role"] = role
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect.")