from flask import Flask, render_template_string, request, redirect, session
import sqlite3
import random
import os

app = Flask(__name__)
app.secret_key = 'deleted_block_fixed_final_2026'

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# La base de datos se guardará en la carpeta 'web' junto al código
DB_PATH = os.path.join(BASE_DIR, 'sistema.db')

# --- INICIALIZADOR DE BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Crear tablas necesarias
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
        (user TEXT PRIMARY KEY, pass TEXT, rol TEXT, creditos INTEGER, creado_por TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pedidos 
        (id_pedido INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, numero TEXT, 
        estado TEXT, nombres TEXT, dni TEXT, imei TEXT, c_bloq TEXT, 
        operador_tel TEXT, plan TEXT, equipo TEXT)''')
    
    # Crear tu usuario administrador si no existe
    cursor.execute("SELECT * FROM usuarios WHERE user='jhorny'")
    if not cursor.fetchone():
        # Usuario: jhorny | Pass: 123456
        cursor.execute("INSERT INTO usuarios (user, pass, rol, creditos, creado_por) 
                       VALUES ('jhorny', '123456', 'superadmin', 999999, 'SYSTEM')")
    
    conn.commit()
    conn.close()

# Ejecutar creación de tablas al arrancar
init_db()

# --- FUNCIÓN DE DISEÑO ---
def layout(content, show_nav=False):
    u, r = session.get('user'), session.get('rol')
    is_boss = (u == 'jhorny')
    is_admin = (r == 'admin')
    
    nav = ""
    if show_nav:
        nav = f"""
        <div class="w-full border border-red-900/50 rounded-2xl p-4 flex justify-between items-center mb-8 bg-[#0d0d0d] relative z-40 shadow-lg shadow-red-900/10">
            <div class="flex items-center gap-2">
                <div class="w-6 h-6 bg-black rounded-full border border-red-500 flex items-center justify-center"><span class="text-[9px] font-bold italic text-red-500">D</span></div>
                <span class="text-[9px] text-red-500 font-bold italic uppercase tracking-widest">DELETED BLOCK</span>
            </div>
            <button onclick="toggleMenu()" class="text-gray-400"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path></svg></button>
        </div>
        <div id="sidebar" class="fixed top-0 right-0 h-full w-64 bg-[#0a0a0a] border-l border-red-900/30 transform translate-x-full transition-transform duration-300 ease-in-out z-50 p-6 shadow-2xl">
            <div class="flex justify-between items-center mb-10"><span class="text-xs font-bold text-red-500 uppercase tracking-widest">Menú de Control</span><button onclick="toggleMenu()" class="text-white text-2xl">&times;</button></div>
            <div class="flex flex-col gap-6">
                <a href="/" class="text-xs font-bold uppercase text-blue-400">🏠 Inicio</a>
                {f"<a href='/panel_admin' class='text-xs font-bold uppercase text-red-500 font-black tracking-widest'>💎 PANEL ADMIN</a>" if is_boss or is_admin else ""}
                <a href="/planes" class="text-xs font-bold uppercase text-purple-400 font-black">🛒 Comprar Créditos</a>
                <a href="/bloqueo" class="text-xs font-bold uppercase text-gray-400">🚫 Bloqueo</a>
                <a href="/soporte" class="text-xs font-bold uppercase text-green-500">🎧 Soporte</a>
                <hr class="border-gray-900"><a href="/logout" class="text-xs font-bold uppercase text-white">🚪 Salir</a>
            </div>
        </div>
        <div id="overlay" onclick="toggleMenu()" class="fixed inset-0 bg-black/70 hidden z-40"></div>
        """
    
    return f"""<!DOCTYPE html><html lang="es"><head><script src="https://cdn.tailwindcss.com"></script><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><style>body {{ background-color: #050505; color: white; font-family: sans-serif; touch-action: manipulation; overflow-x: hidden; }}.neon-card {{ background: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 20px; }}.input-dark {{ background: #141414; border: 1px solid #222; border-radius: 12px; padding: 12px; width: 100%; outline: none; color: white; }}</style><script>function toggleMenu() {{ document.getElementById('sidebar').classList.toggle('translate-x-full'); document.getElementById('overlay').classList.toggle('hidden'); }}</script></head><body class="min-h-screen p-4 flex flex-col items-center"><div class="w-full max-w-sm">{nav}{content}</div></body></html>"""

@app.route('/')
def index():
    if 'user' not in session: return redirect('/login')
    conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
    cursor.execute("SELECT creditos FROM usuarios WHERE user=?", (session['user'],))
    rest = cursor.fetchone()[0]
    return layout(f"""
        <div class="flex flex-col items-center mb-6 mt-4"><div class="w-16 h-16 bg-black rounded-full border-2 border-red-900 flex items-center justify-center mb-2 shadow-2xl shadow-red-900/20"><span class="text-3xl font-bold italic text-red-600">D</span></div><h1 class="text-lg font-bold tracking-widest uppercase">DELETED BLOCK</h1></div>
        <div class="neon-card p-4 text-center border-b-4 border-red-600 mb-6"><p class="text-[8px] text-gray-500 uppercase font-bold">Créditos Restantes</p><h2 class="text-2xl font-bold">{rest}</h2></div>
        <div class="neon-card p-5"><h3 class="text-[9px] font-bold text-red-400 uppercase mb-4 text-center border-b border-gray-900 pb-2">Historial</h3><p class='text-center text-gray-600 text-[10px] py-4'>Bienvenido al sistema.</p></div>
    """, True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('cap') == str(session.get('captcha_val')):
            u, p = request.form['u'], request.form['p']
            conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
            cursor.execute("SELECT rol FROM usuarios WHERE user=? AND pass=?", (u, p))
            res = cursor.fetchone()
            if res:
                session['user'], session['rol'] = u, res[0]
                return redirect('/')
    session['captcha_val'] = random.randint(100000, 999999)
    return layout(f"""<div class="flex flex-col items-center mt-12"><div class="w-20 h-20 bg-black rounded-full border-4 border-red-900 flex items-center justify-center mb-4 shadow-2xl"><span class="text-4xl font-bold italic text-white">D</span></div><h1 class="text-xl font-bold mb-1 uppercase tracking-widest text-white">DELETED BLOCK</h1><form method="post" class="w-full space-y-4 mt-4"><input name="u" placeholder="Usuario" class="input-dark" autocomplete="off"><input name="p" type="password" placeholder="Contraseña" class="input-dark"><div class="flex gap-2"><div class="bg-white text-black p-3 rounded-xl font-mono font-bold w-1/2 text-center text-lg">{session['captcha_val']}</div><input name="cap" placeholder="Captcha" class="input-dark w-1/2 text-center" autocomplete="off"></div><button class="w-full bg-red-800 p-4 rounded-2xl font-bold text-sm uppercase shadow-lg shadow-red-900/40">Acceder</button></form></div>""", False)

@app.route('/logout')
def logout(): session.clear(); return redirect('/login')

@app.route('/panel_admin', methods=['GET', 'POST'])
def panel_admin():
    if session.get('user') != 'jhorny': return redirect('/')
    conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
    if request.method == 'POST':
        action = request.form['action']
        if action == 'crear':
            cursor.execute("INSERT INTO usuarios (user, pass, rol, creditos, creado_por) VALUES (?, ?, ?, 0, ?)", 
                           (request.form['u'], request.form['p'], 'user', 'jhorny'))
            conn.commit()
    cursor.execute("SELECT user, creditos FROM usuarios")
    users = cursor.fetchall()
    lista = "".join([f'<div class="flex justify-between text-[10px] p-2 border-b border-gray-900"><span>{u[0]}</span><span class="text-red-500">{u[1]} Cr.</span></div>' for u in users])
    return layout(f"<div class='neon-card p-6 mt-4'><h2 class='text-xs text-red-500 font-bold mb-4 uppercase'>Admin Panel</h2><form method='POST' class='space-y-2 mb-4'><input type='hidden' name='action' value='crear'><input name='u' placeholder='Usuario' class='input-dark text-xs'><input name='p' placeholder='Pass' class='input-dark text-xs'><button class='w-full bg-blue-700 p-2 rounded-lg text-[10px]'>CREAR</button></form><div>{lista}</div></div>", True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

