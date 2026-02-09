from flask import Flask, render_template_string, request, redirect, session
import sqlite3
import random
import os

app = Flask(__name__)
app.secret_key = 'deleted_block_fixed_final_2026'

# --- CORRECCIÓN DE RUTAS PARA RENDER ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# La DB se guardará en la misma carpeta que el código para evitar errores de permisos
DB_PATH = os.path.join(BASE_DIR, 'sistema.db')

# --- INICIALIZADOR AUTOMÁTICO (Para que no falle al iniciar) ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
        (user TEXT PRIMARY KEY, pass TEXT, rol TEXT, creditos INTEGER, creado_por TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pedidos 
        (id_pedido INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, numero TEXT, 
        estado TEXT, nombres TEXT, dni TEXT, imei TEXT, c_bloq TEXT, 
        operador_tel TEXT, plan TEXT, equipo TEXT)''')
    
    # Crear tu usuario administrador si no existe
    cursor.execute("SELECT * FROM usuarios WHERE user='jhorny'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios VALUES ('jhorny', '123456', 'superadmin', 999999, 'SYSTEM')")
    conn.commit()
    conn.close()

init_db()

# --- FUNCIÓN DE DISEÑO (TU LAYOUT ORIGINAL) ---
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
                {f"<a href='/gestion' class='text-xs font-bold uppercase text-yellow-500'>⚙️ Gestión Pedidos</a>" if is_boss or r == 'operador' else ""}
                <a href="/planes" class="text-xs font-bold uppercase text-purple-400 font-black">🛒 Comprar Créditos</a>
                <a href="/bloqueo" class="text-xs font-bold uppercase text-gray-400">🚫 Bloqueo</a>
                <a href="/soporte" class="text-xs font-bold uppercase text-green-500">🎧 Soporte</a>
                <hr class="border-gray-900"><a href="/logout" class="text-xs font-bold uppercase text-white">🚪 Salir</a>
            </div>
        </div>
        <div id="overlay" onclick="toggleMenu()" class="fixed inset-0 bg-black/70 hidden z-40"></div>
        """
    
    modal_script = """
    <script>
        function toggleMenu() { document.getElementById('sidebar').classList.toggle('translate-x-full'); document.getElementById('overlay').classList.toggle('hidden'); }
        function showReport(nombres, dni, imei, cb, operador, plan, equipo) {
            document.getElementById('rep_nombres').innerText = nombres;
            document.getElementById('rep_dni').innerText = dni;
            document.getElementById('rep_imei').innerText = imei;
            document.getElementById('rep_cb').innerText = cb;
            document.getElementById('rep_ope').innerText = operador;
            document.getElementById('rep_plan').innerText = plan;
            document.getElementById('rep_equipo').innerText = equipo;
            document.getElementById('modalReport').classList.remove('hidden');
        }
        function closeReport() {
            document.getElementById('modalReport').classList.add('hidden');
        }
    </script>
    """

    modal_html = """
    <div id="modalReport" class="hidden fixed inset-0 bg-black/90 z-[60] flex items-center justify-center p-4">
        <div class="bg-[#0f0f0f] border border-red-600/50 w-full max-w-xs rounded-2xl p-6 shadow-2xl shadow-red-900/50 relative">
            <button onclick="closeReport()" class="absolute top-3 right-4 text-red-500 font-bold text-xl">&times;</button>
            <div class="text-center mb-6">
                <div class="w-12 h-12 bg-black rounded-full border-2 border-red-600 flex items-center justify-center mx-auto mb-2"><span class="text-xl font-bold italic text-red-600">D</span></div>
                <h3 class="text-red-500 font-bold uppercase tracking-widest text-xs">Reporte Oficial</h3>
                <p class="text-[8px] text-gray-500 uppercase">Deleted Block System</p>
            </div>
            <div class="space-y-3 text-[10px] font-mono text-gray-300">
                <div class="flex justify-between border-b border-gray-800 pb-1"><span>NOMBRES:</span> <span id="rep_nombres" class="text-white font-bold text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span>DNI:</span> <span id="rep_dni" class="text-white font-bold text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span>OPERADOR:</span> <span id="rep_ope" class="text-blue-400 font-bold text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span>PLAN:</span> <span id="rep_plan" class="text-yellow-500 font-bold text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span>EQUIPO:</span> <span id="rep_equipo" class="text-white font-bold text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span>IMEI:</span> <span id="rep_imei" class="text-red-400 font-bold text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span>COD. BLOQUEO:</span> <span id="rep_cb" class="text-green-500 font-bold text-right"></span></div>
            </div>
            <button onclick="closeReport()" class="w-full mt-4 bg-red-900/30 text-red-500 border border-red-900 rounded-xl py-2 text-[10px] uppercase font-bold">Cerrar</button>
        </div>
    </div>
    """

    return f"""<!DOCTYPE html><html lang="es"><head><script src="https://cdn.tailwindcss.com"></script><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><style>body {{ background-color: #050505; color: white; font-family: sans-serif; touch-action: manipulation; overflow-x: hidden; }}.neon-card {{ background: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 20px; }}.input-dark {{ background: #141414; border: 1px solid #222; border-radius: 12px; padding: 12px; width: 100%; outline: none; color: white; }}</style>{modal_script}</head><body class="min-h-screen p-4 flex flex-col items-center"><div class="w-full max-w-sm">{nav}{content}</div>{modal_html}</body></html>"""

# --- TODAS TUS RUTAS ORIGINALES ---

@app.route('/')
def index():
    if 'user' not in session: return redirect('/login')
    conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
    cursor.execute("SELECT creditos FROM usuarios WHERE user=?", (session['user'],))
    rest = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE cliente=? AND estado='EXITOSO'", (session['user'],))
    usados = cursor.fetchone()[0]
    cursor.execute("SELECT numero, estado, nombres, dni, imei, c_bloq, operador_tel, plan, equipo FROM pedidos WHERE cliente=? ORDER BY id_pedido DESC LIMIT 8", (session['user'],))
    peds = cursor.fetchall()
    
    h = ""
    for p in peds:
        btn = ""
        if p[1] == 'EXITOSO':
            btn = f"""<button onclick="showReport('{p[2]}', '{p[3]}', '{p[4]}', '{p[5]}', '{p[6]}', '{p[7]}', '{p[8]}')" class="bg-red-900/20 text-red-500 border border-red-500/50 px-3 py-1 rounded text-[8px] font-bold hover:bg-red-900/50 transition">VER REPORTE</button>"""
        else:
            btn = '<span class="text-[8px] text-yellow-500 italic font-bold tracking-widest">PROCESANDO</span>'
        h += f'<div class="flex justify-between items-center border-b border-gray-900 py-3"><div class="flex flex-col"><span class="text-xs font-mono text-white">{p[0]}</span><span class="text-[8px] text-gray-500 uppercase">{p[1]}</span></div>{btn}</div>'

    return layout(f"""
        <div class="flex flex-col items-center mb-6 mt-4"><div class="w-16 h-16 bg-black rounded-full border-2 border-red-900 flex items-center justify-center mb-2 shadow-2xl shadow-red-900/20"><span class="text-3xl font-bold italic text-red-600">D</span></div><h1 class="text-lg font-bold tracking-widest uppercase">DELETED BLOCK</h1></div>
        <div class="grid grid-cols-2 gap-3 mb-6">
            <div class="neon-card p-4 text-center border-b-4 border-blue-600"><p class="text-[8px] text-gray-500 uppercase font-bold">Usados</p><h2 class="text-2xl font-bold">{usados}</h2></div>
            <div class="neon-card p-4 text-center border-b-4 border-red-600"><p class="text-[8px] text-gray-500 uppercase font-bold">Restantes</p><h2 class="text-2xl font-bold">{rest}</h2></div>
        </div>
        <div class="neon-card p-5"><h3 class="text-[9px] font-bold text-red-400 uppercase mb-4 text-center border-b border-gray-900 pb-2">Historial</h3><div class="space-y-1">{h or "<p class='text-center text-gray-600 text-xs py-4'>Sin historial</p>"}</div></div>
    """, True)

@app.route('/panel_admin', methods=['GET', 'POST'])
def panel_admin():
    u_log, r_log = session.get('user'), session.get('rol')
    if u_log != 'jhorny' and r_log != 'admin': return redirect('/')
    conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
    if request.method == 'POST':
        action = request.form['action']
        if action == 'crear':
            cursor.execute("INSERT INTO usuarios (user, pass, rol, creditos, creado_por) VALUES (?, ?, ?, 0, ?)", 
                           (request.form['u'], request.form['p'], request.form['r'], u_log))
            conn.commit()
        elif action == 'creditos':
            target, cant = request.form['target'], int(request.form['cant'])
            cursor.execute("UPDATE usuarios SET creditos = creditos + ? WHERE user=?", (cant, target))
            conn.commit()

    cursor.execute("SELECT user, creditos, rol FROM usuarios" if u_log == 'jhorny' else "SELECT user, creditos, rol FROM usuarios WHERE creado_por=?", (u_log,))
    lista = "".join([f'<div class="flex justify-between text-[10px] p-3 border-b border-gray-900"><span>{u[0]} <b class="text-gray-600">({u[2]})</b></span><span class="text-red-500 font-bold">{u[1]} Cr.</span></div>' for u in cursor.fetchall()])
    return layout(f"""<div class="neon-card p-6 mt-4"><h2 class="text-[10px] text-red-500 font-bold uppercase text-center mb-6">Panel Admin</h2><form method="POST" class="space-y-3 mb-6"><input type="hidden" name="action" value="crear"><input name="u" placeholder="Usuario" class="input-dark text-xs"><input name="p" placeholder="Pass" class="input-dark text-xs"><select name="r" class="input-dark text-xs bg-[#141414]"><option value="user">Cliente</option><option value="operador">Operador</option></select><button class="w-full bg-blue-700 p-3 rounded-xl font-bold text-[9px]">REGISTRAR</button></form><form method="POST" class="space-y-3"><input type="hidden" name="action" value="creditos"><input name="target" placeholder="Usuario Destino" class="input-dark text-xs"><input name="cant" type="number" placeholder="Cantidad" class="input-dark text-xs"><button class="w-full bg-red-700 p-3 rounded-xl font-bold text-[9px]">CARGAR SALDO</button></form><div class="mt-6">{lista}</div></div>""", True)

@app.route('/gestion')
def gestion():
    if session.get('rol') not in ['operador', 'superadmin', 'admin'] and session.get('user') != 'jhorny': return redirect('/')
    conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
    cursor.execute("SELECT id_pedido, cliente, numero FROM pedidos WHERE estado='PENDIENTE'")
    ps = cursor.fetchall()
    l = "".join([f'<div class="neon-card p-4 mb-3 flex justify-between items-center"><div><p class="text-[7px] text-gray-500">CLIENTE: {p[1]}</p><p class="text-lg font-mono">{p[2]}</p></div><a href="/trabajar/{p[0]}" class="bg-yellow-600 text-black px-4 py-2 rounded-xl text-[10px] font-black">AGARRAR</a></div>' for p in ps])
    return layout(f"<h2 class='text-center text-[10px] text-yellow-500 font-bold mt-10 mb-6 uppercase'>Bandeja Operador</h2>{l or '<p class=\"text-center text-gray-600 py-10 text-xs\">Sin pendientes</p>'}", True)

@app.route('/trabajar/<int:id_p>')
def trabajar(id_p):
    conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
    cursor.execute("SELECT id_pedido, cliente, numero FROM pedidos WHERE id_pedido=?", (id_p,))
    p = cursor.fetchone()
    return layout(f"""<div class="neon-card p-6 mt-10"><h2 class="text-center text-[10px] text-yellow-500 font-bold mb-6">LLENAR: {p[2]}</h2><form action="/completar" method="POST" class="space-y-3"><input type="hidden" name="id_p" value="{p[0]}"><input name="nom" placeholder="NOMBRES" class="input-dark text-xs" required><input name="dni" placeholder="DNI" class="input-dark text-xs" required><input name="ope" placeholder="OPERADOR" class="input-dark text-xs" required><input name="plan" placeholder="PLAN" class="input-dark text-xs" required><input name="equ" placeholder="EQUIPO" class="input-dark text-xs" required><input name="imei" placeholder="IMEI" class="input-dark text-xs" required><input name="cb" placeholder="C.BLOQ" class="input-dark text-xs" required><button class="w-full bg-green-600 p-4 rounded-xl font-black text-[10px] uppercase">Enviar Reporte</button></form></div>""", True)

@app.route('/completar', methods=['POST'])
def completar():
    conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET nombres=?, dni=?, imei=?, c_bloq=?, operador_tel=?, plan=?, equipo=?, estado='EXITOSO' WHERE id_pedido=?", 
                   (request.form['nom'], request.form['dni'], request.form['imei'], request.form['cb'], request.form['ope'], request.form['plan'], request.form['equ'], request.form['id_p']))
    conn.commit()
    return redirect('/gestion')

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
    return layout(f"""<div class="flex flex-col items-center mt-12"><div class="w-20 h-20 bg-black rounded-full border-4 border-red-900 flex items-center justify-center mb-4 shadow-2xl"><span class="text-4xl font-bold italic text-white">D</span></div><h1 class="text-xl font-bold mb-1 uppercase tracking-widest text-white">DELETED BLOCK</h1><form method="post" class="w-full space-y-4 mt-4"><input name="u" placeholder="Usuario" class="input-dark" autocomplete="off"><input name="p" type="password" placeholder="Contraseña" class="input-dark"><div class="flex gap-2"><div class="bg-white text-black p-3 rounded-xl font-mono font-bold w-1/2 text-center text-lg">{session['captcha_val']}</div><input name="cap" placeholder="Captcha" class="input-dark w-1/2 text-center" autocomplete="off"></div><button class="w-full bg-red-800 p-4 rounded-2xl font-bold text-sm uppercase shadow-lg shadow-red-900/40">Acceder</button></form><a href="https://t.me/Angel_dox1" class="mt-8 text-red-400 text-xs font-bold uppercase tracking-widest flex items-center gap-2 italic"><span>👤</span> CONTACTAR VENDEDOR</a></div>""", False)

@app.route('/logout')
def logout(): session.clear(); return redirect('/login')

@app.route('/planes')
def planes():
    precios = [("01 CRÉDITO", "S/15.00"), ("04 CRÉDITOS", "S/60.00"), ("06 CRÉDITOS", "S/90.00"), ("10 CRÉDITOS", "S/150.00"), ("12 CRÉDITOS", "S/120.00"), ("20 CRÉDITOS", "S/200.00")]
    cards = "".join([f'<div class="neon-card p-4 mb-3 border-l-4 border-red-600 flex justify-between items-center"><div><p class="text-sm font-bold uppercase">{p[0]}</p><p class="text-[10px] text-gray-500 font-mono">{p[1]}</p></div><a href="https://t.me/Angel_dox1?text=Comprar+{p[0].replace(" ","+")}" class="bg-gradient-to-r from-purple-600 to-pink-600 px-4 py-2 rounded-xl text-[9px] font-bold text-white shadow-lg">COMPRAR</a></div>' for p in precios])
    return layout(f"<h2 class='text-center text-[10px] text-red-500 font-bold mt-10 mb-6 uppercase tracking-widest italic'>Paquetes Oficiales</h2>{cards}", True)

@app.route('/bloqueo')
def bloqueo():
    return layout(f"""<div class="neon-card p-6 mt-10 text-center"><h2 class="text-[10px] text-red-400 font-bold mb-6 uppercase italic">Solicitar Bloqueo</h2><form action="/solicitar" method="POST" class="space-y-4"><div class="bg-black p-5 rounded-2xl border border-gray-800"><input type="text" name="num" placeholder="9XXXXXXXX" maxlength="9" class="bg-transparent w-full text-center text-4xl font-mono text-white outline-none" required></div><button class="w-full bg-red-800 p-4 rounded-2xl font-bold text-sm uppercase">Enviar Solicitud</button></form></div>""", True)

@app.route('/solicitar', methods=['POST'])
def solicitar():
    if 'user' in session:
        conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
        cursor.execute("SELECT creditos FROM usuarios WHERE user=?", (session['user'],))
        res = cursor.fetchone()
        if res and res[0] > 0:
            cursor.execute("UPDATE usuarios SET creditos = creditos - 1 WHERE user=?", (session['user'],))
            cursor.execute("INSERT INTO pedidos (cliente, numero, estado) VALUES (?, ?, 'PENDIENTE')", (session['user'], request.form['num']))
            conn.commit()
    return redirect('/')

@app.route('/soporte')
def soporte():
    return layout(f"""<div class="neon-card p-8 mt-10 text-center border-t-2 border-green-500"><h2 class="text-xl font-bold mb-2 uppercase italic text-white">Soporte 24/7</h2><a href="https://t.me/Angel_dox1" class="inline-block w-full bg-green-600 p-4 rounded-3xl font-bold text-white uppercase text-xs">Ir a Telegram</a></div>""", True)

if __name__ == '__main__':
    # --- CORRECCIÓN DE PUERTO PARA RENDER ---
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
 
