import sqlite3
import os

os.makedirs('database', exist_ok=True)

def setup_db():
    conn = sqlite3.connect('database/sistema.db')
    cursor = conn.cursor()
    # Tabla de Usuarios
    cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT UNIQUE, pass TEXT, rol TEXT, creditos INTEGER DEFAULT 0)')
    # Tabla de Pedidos
    cursor.execute('CREATE TABLE IF NOT EXISTS pedidos (id_pedido INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, numero TEXT, nombres TEXT, dni TEXT, imei TEXT, c_bloq TEXT, estado TEXT DEFAULT "PENDIENTE", encargado TEXT)')
    # Usuario Jefe (Tú)
    try: cursor.execute("INSERT INTO usuarios (user, pass, rol, creditos) VALUES ('jhorny', 'admin123', 'super', 9999)")
    except: pass
    # Usuario Trabajador (Tu encargado)
    try: cursor.execute("INSERT INTO usuarios (user, pass, rol) VALUES ('operador1', '1234', 'encargado')")
    except: pass
    conn.commit()
    conn.close()
    print("✅ Base de datos lista.")

if __name__ == "__main__":
    setup_db()

