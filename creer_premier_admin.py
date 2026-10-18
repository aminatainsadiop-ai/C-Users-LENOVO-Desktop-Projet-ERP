import hashlib
from database import get_connection

nom = "Diop"
prenom = "Admin"
email = "admin@escoa.sn"
mot_de_passe = "DIOP"  # change-le si tu veux
role = "Administrateur"

hash_password = hashlib.sha256(mot_de_passe.encode()).hexdigest()

conn = get_connection()
cur = conn.cursor()
cur.execute("""
    INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role)
    VALUES (%s, %s, %s, %s, %s)
""", (nom, prenom, email, hash_password, role))
conn.commit()
conn.close()

print("Administrateur créé avec succès.")