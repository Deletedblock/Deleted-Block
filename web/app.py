from flask import Flask, render_template_string, request, redirect, session
import sqlite3
import random
import os

app = Flask(__name__)
app.secret_key = 'deleted_block_fixed_final_2026'

# --- CORRECCIÓN DE RUTA PARA RENDER ---
# Esto detecta la carpeta actual donde esté el código
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Busca la base de datos dentro de una carpeta 'database' en tu proyecto
DB_PATH = os.path.join(BASE_DIR, 'database', 'sistema.db')

# Asegurarse de que la carpeta database existe (evita errores en Render)
if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH))

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
            btn = f"""<button onclick="showReport('{p[2]}', '{p[3]}', '{p[4]}', '{p[5]}', '{p[6]}', '{p[7]}', '{p[8]}')" class="bg-red-900/20 text-red-500 border border-red-500/50 px-3 py-1 rounded text-[8px] font-bold">VER REPORTE</button>"""
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
    u_log = session.get('user')
    r_log = session.get('rol')
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
            if u_log != 'jhorny': cursor.execute("UPDATE usuarios SET creditos = creditos - ? WHERE user=?", (cant, u_log))
            conn.commit()

    cursor.execute("SELECT user, creditos, rol FROM usuarios" if u_log == 'jhorny' else "SELECT user, creditos, rol FROM usuarios WHERE creado_por=?", (u_log,))
    users = cursor.fetchall()
    lista = "".join([f'<div class="flex justify-between text-[10px] p-3 border-b border-gray-900"><span>{u[0]} <b class="text-gray-600">({u[2]})</b></span><span class="text-red-500 font-bold">{u[1]} Cr.</span></div>' for u in users])

    return layout(f"""
        <div class="neon-card p-6 mt-4">
            <h2 class="text-[10px] text-red-500 font-bold uppercase text-center mb-6">Panel ({r_log})</h2>
            <form method="POST" class="space-y-3 mb-8 border-b border-gray-800 pb-6">
                <input type="hidden" name="action" value="crear"><input name="u" placeholder="Usuario Nuevo" class="input-dark text-xs" required><input name="p" placeholder="Contraseña" class="input-dark text-xs" required>
                <select name="r" class="input-dark text-xs bg-[#141414]"><option value="user">Cliente</option><option value="operador">Operador</option></select><button class="w-full bg-blue-700 p-3 rounded-xl font-bold text-[9px]">Registrar</button>
            </form>
            <form method="POST" class="space-y-3 mb-8 border-b border-gray-800 pb-6">
                <input type="hidden" name="action" value="creditos"><input name="target" placeholder="Usuario Destino" class="input-dark text-xs" required><input name="cant" type="number" placeholder="Cantidad" class="input-dark text-xs" required><button class="w-full bg-red-700 p-3 rounded-xl font-bold text-[9px]">Enviar Créditos</button>
            </form>
            <div class="max-h-60 overflow-y-auto">{lista}</div>
        </div>
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
    return layout(f"""<div class="flex flex-col items-center mt-12"><div class="w-20 h-20 bg-black rounded-full border-4 border-red-900 flex items-center justify-center mb-4"><span class="text-4xl font-bold italic text-white">D</span></div><h1 class="text-xl font-bold mb-1 uppercase text-white">DELETED BLOCK</h1><form method="post" class="w-full space-y-4 mt-4"><input name="u" placeholder="Usuario" class="input-dark" autocomplete="off"><input name="p" type="password" placeholder="Contraseña" class="input-dark"><div class="flex gap-2"><div class="bg-white text-black p-3 rounded-xl font-mono font-bold w-1/2 text-center">{session['captcha_val']}</div><input name="cap" placeholder="Captcha" class="input-dark w-1/2 text-center" autocomplete="off"></div><button class="w-full bg-red-800 p-4 rounded-2xl font-bold text-sm">Acceder</button></form></div>""", False)

# --- VISTAS FALTANTES REDUCIDAS ---
@app.route('/logout')
def logout(): session.clear(); return redirect('/login')

@app.route('/planes')
def planes(): return layout("<h2 class='text-center text-red-500 font-bold mt-10'>PAQUETES DISPONIBLES EN TELEGRAM</h2>", True)

@app.route('/bloqueo')
def bloqueo(): return layout("<h2 class='text-center text-red-500 font-bold mt-10'>MÓDULO DE BLOQUEO ACTIVO</h2>", True)

@app.route('/soporte')
def soporte(): return layout("<h2 class='text-center text-green-500 font-bold mt-10'>SOPORTE 24/7</h2>", True)

if __name__ == '__main__':
    # --- CORRECCIÓN DE PUERTO PARA RENDER ---
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
