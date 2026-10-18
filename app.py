import streamlit as st
from login import login_page
from database import get_connection

st.set_page_config(
    page_title="ERP ESCOA",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Fichier de style non trouvé.")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_page()
    st.stop()

with st.sidebar:
    if st.button("Déconnexion"):
        st.session_state["authenticated"] = False
        st.rerun()

st.markdown("""
<div class="header">
    <h1>ERP ESCOA</h1>
    <p>Système de gestion de l'École Supérieure de Commerce et d'Administration</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## Bienvenue")
st.markdown("---")

# ---------------- FONCTION DE COMPTAGE ----------------
def compter(table):
    # COUNT(*) est plus rapide que de récupérer toutes les lignes juste pour les compter
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    result = cur.fetchone()[0]  # fetchone() retourne un tuple (ex: (5,)), donc [0] extrait le nombre
    conn.close()
    return result

# ---------------- STATISTIQUES ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Étudiants", compter("etudiants"))
with col2:
    st.metric("Enseignants", compter("enseignants"))
with col3:
    st.metric("Filières", compter("filieres"))
with col4:
    st.metric("Matières", compter("matieres"))

st.markdown("---")
st.info("Sélectionnez un module dans le menu situé à gauche.")