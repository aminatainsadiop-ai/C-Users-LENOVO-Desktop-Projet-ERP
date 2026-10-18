import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="ecole",
        user="postgres",
        password="DIOP",
        port="5432"
    )
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("Connexion réussie à PostgreSQL !")
        conn.close()
    except Exception as e:
        print("Erreur :", e)