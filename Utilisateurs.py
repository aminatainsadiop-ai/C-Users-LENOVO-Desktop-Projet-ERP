import streamlit as st
import pandas as pd
import hashlib
from database import get_connection

st.set_page_config(page_title="Utilisateurs - ERP ESCOA", layout="wide")

if not st.session_state.get("authenticated", False):
    st.error("Veuillez vous connecter d'abord.")
    st.stop()

try:
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown("""
<div class="header">
    <h1>Gestion des Utilisateurs</h1>
    <p>Créer et gérer les comptes ayant accès à l'ERP</p>
</div>
""", unsafe_allow_html=True)

# ---------------- FONCTIONS BASE DE DONNÉES ----------------

def get_utilisateurs():
    conn = get_connection()
    cur = conn.cursor()
    # On ne sélectionne jamais mot_de_passe ici, pour ne jamais l'afficher à l'écran
    cur.execute("""
        SELECT id_utilisateur, nom, prenom, email, role
        FROM utilisateurs
        ORDER BY nom
    """)
    result = cur.fetchall()
    conn.close()
    return result

def add_utilisateur(nom, prenom, email, mot_de_passe, role):
    hash_password = hashlib.sha256(mot_de_passe.encode()).hexdigest()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role)
        VALUES (%s, %s, %s, %s, %s)
    """, (nom, prenom, email, hash_password, role))
    conn.commit()
    conn.close()

def update_utilisateur(id_utilisateur, nom, prenom, email, role, nouveau_mot_de_passe=None):
    conn = get_connection()
    cur = conn.cursor()
    if nouveau_mot_de_passe:
        # Si un nouveau mot de passe est fourni, on le hache et on le met à jour aussi
        hash_password = hashlib.sha256(nouveau_mot_de_passe.encode()).hexdigest()
        cur.execute("""
            UPDATE utilisateurs
            SET nom = %s, prenom = %s, email = %s, role = %s, mot_de_passe = %s
            WHERE id_utilisateur = %s
        """, (nom, prenom, email, role, hash_password, id_utilisateur))
    else:
        # Sinon on garde l'ancien mot de passe inchangé
        cur.execute("""
            UPDATE utilisateurs
            SET nom = %s, prenom = %s, email = %s, role = %s
            WHERE id_utilisateur = %s
        """, (nom, prenom, email, role, id_utilisateur))
    conn.commit()
    conn.close()

def delete_utilisateur(id_utilisateur):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM utilisateurs WHERE id_utilisateur = %s", (id_utilisateur,))
    conn.commit()
    conn.close()

ROLES = ["Administrateur", "Enseignant", "Étudiant", "Secrétariat"]

# ---------------- ÉTAT ----------------
if "edit_id_utilisateur" not in st.session_state:
    st.session_state["edit_id_utilisateur"] = None

utilisateurs = get_utilisateurs()
utilisateur_a_modifier = None
if st.session_state["edit_id_utilisateur"] is not None:
    utilisateur_a_modifier = next((u for u in utilisateurs if u[0] == st.session_state["edit_id_utilisateur"]), None)

titre_form = "Modifier l'utilisateur" if utilisateur_a_modifier else "Ajouter un utilisateur"

# ---------------- FORMULAIRE D'AJOUT / MODIFICATION ----------------
with st.expander(titre_form, expanded=(utilisateur_a_modifier is not None)):
    with st.form("form_utilisateur", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom", value=utilisateur_a_modifier[1] if utilisateur_a_modifier else "")
            prenom = st.text_input("Prénom", value=utilisateur_a_modifier[2] if utilisateur_a_modifier else "")
            email = st.text_input("Email", value=utilisateur_a_modifier[3] if utilisateur_a_modifier else "")
        with col2:
            role_index = ROLES.index(utilisateur_a_modifier[4]) if (utilisateur_a_modifier and utilisateur_a_modifier[4] in ROLES) else 0
            role = st.selectbox("Rôle", ROLES, index=role_index)

            # En modification, le mot de passe est optionnel : on ne le change que si rempli
            label_password = "Nouveau mot de passe (laisser vide pour ne pas changer)" if utilisateur_a_modifier else "Mot de passe"
            mot_de_passe = st.text_input(label_password, type="password")

        col_submit, col_cancel = st.columns([1, 1])
        with col_submit:
            submit = st.form_submit_button("Enregistrer")
        with col_cancel:
            cancel = st.form_submit_button("Annuler") if utilisateur_a_modifier else False

        if cancel:
            st.session_state["edit_id_utilisateur"] = None
            st.rerun()

        if submit:
            if not nom or not prenom or not email:
                st.error("Nom, prénom et email sont obligatoires.")
            elif not utilisateur_a_modifier and not mot_de_passe:
                st.error("Le mot de passe est obligatoire pour un nouvel utilisateur.")
            else:
                try:
                    if utilisateur_a_modifier:
                        update_utilisateur(
                            utilisateur_a_modifier[0], nom, prenom, email, role,
                            nouveau_mot_de_passe=mot_de_passe if mot_de_passe else None
                        )
                        st.success(f"Utilisateur {prenom} {nom} modifié avec succès.")
                        st.session_state["edit_id_utilisateur"] = None
                    else:
                        add_utilisateur(nom, prenom, email, mot_de_passe, role)
                        st.success(f"Utilisateur {prenom} {nom} ajouté avec succès.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

st.markdown("---")

# ---------------- TABLEAU DES UTILISATEURS ----------------
st.subheader("Liste des utilisateurs")

if not utilisateurs:
    st.info("Aucun utilisateur enregistré pour le moment.")
else:
    df = pd.DataFrame(utilisateurs, columns=["ID", "Nom", "Prénom", "Email", "Rôle"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### Modifier ou supprimer un utilisateur")
    options = {f"{u[1]} {u[2]} - {u[4]} (ID {u[0]})": u[0] for u in utilisateurs}
    selection = st.selectbox("Sélectionner un utilisateur", list(options.keys()))
    selected_id = options[selection]

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("✏️ Modifier la sélection"):
            st.session_state["edit_id_utilisateur"] = selected_id
            st.rerun()
    with col2:
        if st.button("🗑️ Supprimer la sélection"):
            try:
                delete_utilisateur(selected_id)
                st.success("Utilisateur supprimé.")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")