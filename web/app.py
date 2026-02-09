import os, random, json
from flask import Flask, request, redirect, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = 'deleted_block_fixed_final_2026'

# --- TUS CREDENCIALES EXACTAS (NO TOCAR) ---
url = "https://jkcxqmvbgzfusvoqjjzs.supabase.co"
key = "sb_publishable_v5htdDBl1jcCA5o9VZ_lXw_0U-jSQCj"

# Conexión a Supabase
try:
    supabase = create_client(url, key)
except Exception as e:
    print(f"Error conectando a Supabase: {e}")

# --- DISEÑO (INTERFAZ) ---
def layout(content, show_nav=False, scripts=""):
    u, r = session.get('user'), session.get('rol')
    nav = ""
    if show_nav:
        nav = f"""
        <div class="w-full border border-red-900/50 rounded-2xl p-4 flex justify-between items-center mb-8 bg-[#0d0d0d] relative z-40 shadow-lg shadow-red-900/10">
            <div class="flex items-center gap-2">
                <div class="w-6 h-6 bg-black rounded-full border border-red-500 flex items-center justify-center"><span class="text-[9px] font-bold italic text-red-500">D</span></div>
                <span class="text-[9px] text-red-500 font-bold italic uppercase tracking-widest">DELETED BLOCK</span>
            </div>
            <button onclick="toggleMenu()" class="text-gray-400"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg></button>
        </div>
        <div id="sidebar" class="fixed top-0 right-0 h-full w-64 bg-[#0a0a0a] border-l border-red-900/30 transform translate-x-full transition-transform duration-300 ease-in-out z-50 p-6">
            <div class="flex justify-between items-center mb-10"><span class="text-xs font-bold text-red-500 uppercase tracking-widest">Menú de Control</span><button onclick="toggleMenu()" class="text-gray-500 text-xl">&times;</button></div>
            <div class="flex flex-col gap-6">
                <a href="/" class="text-xs font-bold uppercase text-blue-400">🏠 Inicio</a>
                {f"<a href='/panel_admin' class='text-xs font-bold uppercase text-red-500 font-black tracking-widest'>💎 PANEL ADMIN</a>" if u == 'jhorny' or r == 'admin' else ""}
                {f"<a href='/gestion' class='text-xs font-bold uppercase text-yellow-500'>⚙️ Gestión Pedidos</a>" if u == 'jhorny' or r == 'operador' else ""}
                <a href="/planes" class="text-xs font-bold uppercase text-purple-400 font-black">🛒 Comprar Créditos</a>
                <a href="/bloqueo" class="text-xs font-bold uppercase text-gray-400">🚫 Bloqueo</a>
                <a href="/soporte" class="text-xs font-bold uppercase text-green-500">🎧 Soporte</a>
                <hr class="border-gray-900"><a href="/logout" class="text-xs font-bold uppercase text-white">🚪 Salir</a>
            </div>
        </div>
        <div id="overlay" onclick="toggleMenu()" class="fixed inset-0 bg-black/70 hidden z-40"></div>
        """
    
    base_scripts = """
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
        function closeReport() { document.getElementById('modalReport').classList.add('hidden'); }
    </script>
    """

    # MODAL HTML (Reporte)
    modal_html = """
    <div id="modalReport" class="fixed inset-0 bg-black/90 hidden z-50 flex items-center justify-center p-4">
        <div class="neon-card w-full max-w-sm p-6 relative bg-[#0a0a0a] border border-red-900/50 rounded-xl">
            <button onclick="closeReport()" class="absolute top-4 right-4 text-red-500 font-bold text-xl">&times;</button>
            <h3 class="text-red-500 font-bold uppercase text-center mb-6 text-sm tracking-widest">Reporte Oficial</h3>
            <div class="space-y-3 text-[10px] font-mono">
                <div class="flex justify-between border-b border-gray-800 pb-1"><span class="text-gray-500">TITULAR:</span><span id="rep_nombres" class="text-white text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span class="text-gray-500">DNI:</span><span id="rep_dni" class="text-blue-400 font-bold text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span class="text-gray-500">IMEI:</span><span id="rep_imei" class="text-white text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span class="text-gray-500">C.BLOQ:</span><span id="rep_cb" class="text-red-500 font-bold text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span class="text-gray-500">OPERADOR:</span><span id="rep_ope" class="text-white text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span class="text-gray-500">PLAN:</span><span id="rep_plan" class="text-white text-right"></span></div>
                <div class="flex justify-between border-b border-gray-800 pb-1"><span class="text-gray-500">EQUIPO:</span><span id="rep_equipo" class="text-white text-right"></span></div>
            </div>
            <button onclick="closeReport()" class="w-full mt-6 bg-red-900/30 text-red-500 py-3 rounded-xl font-bold uppercase text-xs">Cerrar</button>
        </div>
    </div>
    """
    
    return f"""<!DOCTYPE html><html lang="es"><head><script src="https://cdn.tailwindcss.com"></script><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><title>Deleted Block</title><style>.neon-card{{background:linear-gradient(145deg, #0a0a0a, #050505);box-shadow: 0 4px 6px -1px rgba(220, 38, 38, 0.1), 0 2px 4px -1px rgba(220, 38, 38, 0.06);border: 1px solid rgba(127, 29, 29, 0.3);border-radius: 1rem;}}body{{background-color:#000;color:#fff;font-family:'Courier New', monospace;}}</style></head><body class="p-4 max-w-md mx-auto relative min-h-screen">{nav}{content}{modal_html}{base_scripts}{scripts}</body></html>"""

# --- RUTAS ---
@app.route('/')
def index():
    if 'user' not in session: return redirect('/login')
    u_log = session['user']
    try:
        res_u = supabase.table("usuarios").select("creditos").eq("user", u_log).execute()
        rest = res_u.data[0]['creditos'] if res_u.data else 0
        res_c = supabase.table("pedidos").select("*", count="exact").eq("cliente", u_log).eq("estado", "EXITOSO").execute()
        usados = res_c.count if res_c.count is not None else 0
        peds = supabase.table("pedidos").select("*").eq("cliente", u_log).order("id_pedido", desc=True).limit(8).execute().data
    except:
        rest, usados, peds = 0, 0, []

    h = ""
    for p in peds:
        btn = ""
        if p['estado'] == 'EXITOSO':
            btn = f"""<button onclick="showReport('{p.get('nombres','')}','{p.get('dni','')}','{p.get('imei','')}','{p.get('c_bloq','')}','{p.get('operador_tel','')}','{p.get('plan','')}','{p.get('equipo','')}')" class="text-[8px] bg-green-900/30 text-green-500 px-2 py-1 rounded border border-green-900">VER REPORTE</button>"""
        else:
            btn = '<span class="text-[8px] text-yellow-500 italic font-bold tracking-widest">PROCESANDO</span>'
        h += f'<div class="flex justify-between items-center border-b border-gray-900 py-3"><div class="flex flex-col"><span class="text-xs font-mono text-white">{p["numero"]}</span><span class="text-[8px] text-gray-600">{p["created_at"][:10]}</span></div>{btn}</div>'

    return layout(f"""
        <div class="flex flex-col items-center mb-6 mt-4"><div class="w-16 h-16 bg-black rounded-full border-2 border-red-900 flex items-center justify-center mb-2 shadow-2xl shadow-red-500/20"><span class="text-2xl">☠️</span></div><h1 class="text-lg font-bold tracking-widest text-white">DELETED BLOCK</h1><p class="text-[9px] text-gray-500 uppercase tracking-[0.2em]">Panel Usuario</p></div>
        <div class="grid grid-cols-2 gap-3 mb-6">
            <div class="neon-card p-4 text-center border-b-4 border-blue-600"><p class="text-[8px] text-gray-500 uppercase font-bold">Usados</p><h2 class="text-2xl font-bold">{usados}</h2></div>
            <div class="neon-card p-4 text-center border-b-4 border-red-600"><p class="text-[8px] text-gray-500 uppercase font-bold">Restantes</p><h2 class="text-2xl font-bold">{rest}</h2></div>
        </div>
        <div class="neon-card p-5"><h3 class="text-[9px] font-bold text-red-400 uppercase mb-4 text-center border-b border-gray-900 pb-2">Historial</h3><div class="space-y-1">{h or '<p class="text-center text-gray-600 text-[9px] py-4">Sin actividad reciente</p>'}</div></div>
        <a href="https://deleted-block.onrender.com" class="block text-center mt-6 text-[9px] text-gray-600 hover:text-red-500">Deleted Block System v2.0</a>
    """, True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('cap') == str(session.get('captcha_val')):
            u, p = request.form['u'], request.form['p']
            try:
                res = supabase.table("usuarios").select("*").eq("user", u).eq("pass", p).execute()
                if res.data:
                    session['user'], session['rol'] = u, res.data[0]['rol']
                    return redirect('/')
                else:
                    return layout("<p class='text-red-500 mt-4 font-bold uppercase text-xs'>Usuario o Clave incorrecta</p>")
            except Exception as e:
                return layout(f"<p class='text-red-500 mt-4 text-[8px]'>Error DB: {e}</p>")
    session['captcha_val'] = random.randint(100000, 999999)
    return layout(f"""<div class="flex flex-col items-center mt-12"><div class="w-20 h-20 bg-black rounded-full border-4 border-red-900 flex items-center justify-center mb-4 shadow-2xl shadow-red-900/40"><span class="text-3xl text-red-600 font-bold italic">D</span></div><h2 class="text-xl font-bold mb-8 uppercase tracking-widest">Acceso Seguro</h2><form method="POST" class="w-full space-y-4"><input type="text" name="u" placeholder="USUARIO" class="w-full bg-[#0d0d0d] border border-gray-800 rounded-lg p-3 text-xs text-center focus:border-red-500 outline-none text-white uppercase" required><input type="password" name="p" placeholder="CONTRASEÑA" class="w-full bg-[#0d0d0d] border border-gray-800 rounded-lg p-3 text-xs text-center focus:border-red-500 outline-none text-white" required><div class="flex gap-2"><div class="bg-gray-800 p-3 rounded-lg text-white font-mono font-bold tracking-widest text-sm w-1/3 text-center">{session['captcha_val']}</div><input type="text" name="cap" placeholder="CAPTCHA" class="w-2/3 bg-[#0d0d0d] border border-gray-800 rounded-lg p-3 text-xs text-center focus:border-red-500 outline-none text-white" required></div><button type="submit" class="w-full bg-red-900 hover:bg-red-800 text-white font-bold py-3 rounded-lg text-xs uppercase tracking-widest transition-all shadow-lg shadow-red-900/20">Ingresar Sistema</button></form></div>""")

@app.route('/panel_admin', methods=['GET', 'POST'])
def panel_admin():
    u_log, r_log = session.get('user'), session.get('rol')
    if u_log != 'jhorny' and r_log != 'admin': return redirect('/')

    # Variables para el modal de éxito
    new_user_data = None 

    if request.method == 'POST':
        action = request.form['action']
        
        # --- CREAR USUARIO CON MODAL ---
        if action == 'crear':
            new_u = request.form['u']
            new_p = request.form['p']
            try:
                supabase.table("usuarios").insert({
                    "user": new_u, 
                    "pass": new_p, 
                    "rol": request.form['r'], 
                    "creditos": 0, 
                    "creado_por": u_log
                }).execute()
                # Guardamos los datos para mostrarlos en el modal
                new_user_data = {"u": new_u, "p": new_p}
            except Exception as e:
                print(f"Error creando: {e}")

        # --- AGREGAR CRÉDITOS ---
        elif action == 'creditos':
            target, cant = request.form['target'], int(request.form['cant'])
            res = supabase.table("usuarios").select("creditos").eq("user", u_log).execute()
            if u_log == 'jhorny' or (res.data and res.data[0]['creditos'] >= cant):
                res_t = supabase.table("usuarios").select("creditos").eq("user", target).execute()
                if res_t.data:
                    supabase.table("usuarios").update({"creditos": res_t.data[0]['creditos'] + cant}).eq("user", target).execute()
                    if u_log != 'jhorny':
                        supabase.table("usuarios").update({"creditos": res.data[0]['creditos'] - cant}).eq("user", u_log).execute()

    query = supabase.table("usuarios").select("user, creditos, rol")
    if u_log != 'jhorny': query = query.eq("creado_por", u_log)
    users = query.execute().data
    
    # --- GENERAR LISTA DE USUARIOS CON BOTÓN DE CRÉDITOS ---
    lista = ""
    for u in users:
        lista += f"""
        <div class="flex justify-between items-center text-[10px] p-3 border-b border-gray-900">
            <div>
                <span class="block text-white font-bold">{u["user"]}</span>
                <span class="text-[8px] text-gray-500 uppercase">{u["rol"]}</span>
            </div>
            <div class="flex items-center gap-3">
                <span class="text-red-500 font-bold text-xs">{u["creditos"]} cr</span>
                <button onclick="addCredits('{u['user']}')" class="bg-blue-900/40 border border-blue-500 text-blue-400 px-2 py-1 rounded text-[9px] font-bold hover:bg-blue-900/60">+ ADD</button>
            </div>
        </div>
        """

    # --- HTML DEL MODAL DE CUENTA CREADA (Solo se ve si new_user_data existe) ---
    modal_exito = ""
    if new_user_data:
        modal_exito = f"""
        <div id="modalSuccess" class="fixed inset-0 bg-black/95 z-[60] flex items-center justify-center p-4">
            <div class="w-full max-w-sm bg-[#121212] border border-[#a29bfe] rounded-2xl p-6 relative shadow-[0_0_30px_rgba(162,155,254,0.3)] text-center">
                <span onclick="document.getElementById('modalSuccess').remove()" class="absolute top-4 right-4 text-gray-500 cursor-pointer text-xl">&times;</span>
                <h2 class="text-[#a29bfe] font-bold text-lg mb-6">✨ DELETED BLOCK ✨</h2>
                
                <div class="bg-[#1e1e1e] p-3 rounded-lg mb-3 flex justify-between items-center">
                    <span class="text-gray-400 text-xs">👤 Usuario:</span>
                    <strong id="new_u" class="text-white text-xs">{new_user_data['u']}</strong>
                </div>
                
                <div class="bg-[#1e1e1e] p-3 rounded-lg mb-3 flex justify-between items-center">
                    <span class="text-gray-400 text-xs">🔒 Pass:</span>
                    <div class="flex items-center gap-2">
                        <strong id="new_p" class="text-white text-xs">{new_user_data['p']}</strong>
                    </div>
                </div>

                <div class="bg-[#1e1e1e] p-3 rounded-lg mb-4 flex justify-between items-center">
                    <span class="text-gray-400 text-xs">🌐 URL:</span>
                    <a href="https://deleted-block.onrender.com" class="text-blue-400 text-[9px] underline truncate w-32">deleted-block.onrender.com</a>
                </div>

                <button onclick="copyAll('{new_user_data['u']}', '{new_user_data['p']}')" class="w-full bg-[#6c5ce7] text-white font-bold py-3 rounded-xl shadow-lg hover:bg-[#5849be] transition text-xs uppercase">Copiar Todo</button>
                <button onclick="document.getElementById('modalSuccess').remove()" class="w-full mt-2 bg-red-500/20 text-red-400 font-bold py-2 rounded-xl text-xs uppercase">Cerrar</button>
            </div>
        </div>
        """

    # --- JAVASCRIPT ESPECÍFICO DEL PANEL ---
    scripts_admin = f"""
    <script>
        function addCredits(user) {{
            let cant = prompt("¿Cuántos créditos agregar a " + user + "?");
            if (cant != null && cant != "" && !isNaN(cant)) {{
                document.getElementById('target_input').value = user;
                document.getElementById('cant_input').value = cant;
                document.getElementById('form_creditos').submit();
            }}
        }}
        function copyAll(u, p) {{
            const text = `✨ DELETED BLOCK ✨\\n👤 User: ${{u}}\\n🔒 Pass: ${{p}}\\n🌐 Url: https://deleted-block.onrender.com`;
            navigator.clipboard.writeText(text).then(() => {{
                alert('Datos copiados al portapapeles');
            }});
        }}
    </script>
    """

    return layout(f"""
    {modal_exito}
    <div class="neon-card p-6 mt-4">
        <h2 class="text-[10px] text-red-500 font-bold uppercase text-center mb-6 tracking-widest italic">Panel ({r_log})</h2>
        
        <form method="POST" class="space-y-3 mb-8 border-b border-gray-800 pb-8">
            <input type="hidden" name="action" value="crear">
            <div class="grid grid-cols-2 gap-2">
                <input type="text" name="u" placeholder="NUEVO USUARIO" class="bg-[#0d0d0d] border border-gray-800 rounded p-2 text-[10px] text-white uppercase outline-none focus:border-red-500" required>
                <input type="text" name="p" placeholder="CONTRASEÑA" class="bg-[#0d0d0d] border border-gray-800 rounded p-2 text-[10px] text-white outline-none focus:border-red-500" required>
            </div>
            <select name="r" class="w-full bg-[#0d0d0d] border border-gray-800 rounded p-2 text-[10px] text-gray-400 outline-none uppercase">
                <option value="user">Usuario (Cliente)</option>
                <option value="operador">Operador (Trabajador)</option>
                <option value="admin">Administrador (Revendedor)</option>
            </select>
            <button class="w-full bg-red-900 text-white font-bold py-2 rounded text-[10px] uppercase hover:bg-red-800 transition">Crear Usuario</button>
        </form>

        <h3 class="text-[9px] text-gray-500 font-bold uppercase mb-4 text-center">Usuarios Registrados</h3>
        <div class="max-h-64 overflow-y-auto space-y-1">
            {lista or '<p class="text-center text-gray-700 text-[9px]">Sin usuarios creados</p>'}
        </div>
        
        <form id="form_creditos" method="POST" class="hidden">
            <input type="hidden" name="action" value="creditos">
            <input type="hidden" name="target" id="target_input">
            <input type="hidden" name="cant" id="cant_input">
        </form>
    </div>
    """, True, scripts_admin)

@app.route('/gestion')
def gestion():
    if session.get('rol') not in ['operador', 'admin'] and session.get('user') != 'jhorny': return redirect('/')
    ps = supabase.table("pedidos").select("id_pedido, cliente, numero").eq("estado", "PENDIENTE").execute().data
    l = "".join([f'<div class="neon-card p-4 mb-3 flex justify-between items-center"><div><p class="text-[7px] text-gray-500 uppercase">CLIENTE: {p["cliente"]}</p><p class="text-lg font-mono text-white tracking-widest">{p["numero"]}</p></div><a href="/trabajar/{p["id_pedido"]}" class="bg-yellow-600/20 text-yellow-500 text-[9px] font-bold px-3 py-1 rounded border border-yellow-600/50 uppercase">Atender</a></div>' for p in ps])
    return layout(f"<h2 class='text-center text-[10px] text-yellow-500 font-bold mt-10 mb-6 uppercase'>Bandeja Operador</h2>{l or '<p class=\"text-center text-gray-600 text-xs py-10\">No hay pedidos pendientes...</p>'}", True)

@app.route('/trabajar/<int:id_p>')
def trabajar(id_p):
    p = supabase.table("pedidos").select("*").eq("id_pedido", id_p).execute().data[0]
    return layout(f"""<div class="neon-card p-6 mt-10"><h2 class="text-center text-[10px] text-yellow-500 font-bold mb-6 italic uppercase">Llenar: {p['numero']}</h2><form action="/completar" method="POST" class="space-y-3"><input type="hidden" name="id" value="{p['id_pedido']}"><input type="text" name="nom" placeholder="NOMBRES COMPLETOS" class="w-full bg-[#0d0d0d] border border-gray-800 rounded p-3 text-[10px] text-white uppercase outline-none focus:border-yellow-500" required><input type="text" name="dni" placeholder="DNI TITULAR" class="w-full bg-[#0d0d0d] border border-gray-800 rounded p-3 text-[10px] text-white uppercase outline-none focus:border-yellow-500" required><input type="text" name="imei" placeholder="IMEI" class="w-full bg-[#0d0d0d] border border-gray-800 rounded p-3 text-[10px] text-white uppercase outline-none focus:border-yellow-500" required><input type="text" name="cb" placeholder="CÓDIGO DE BLOQUEO" class="w-full bg-[#0d0d0d] border border-gray-800 rounded p-3 text-[10px] text-white uppercase outline-none focus:border-yellow-500" required><div class="grid grid-cols-2 gap-2"><input type="text" name="ope" placeholder="OPERADOR" class="bg-[#0d0d0d] border border-gray-800 rounded p-3 text-[10px] text-white uppercase outline-none focus:border-yellow-500" required><input type="text" name="plan" placeholder="PLAN" class="bg-[#0d0d0d] border border-gray-800 rounded p-3 text-[10px] text-white uppercase outline-none focus:border-yellow-500" required></div><input type="text" name="equipo" placeholder="MODELO EQUIPO" class="w-full bg-[#0d0d0d] border border-gray-800 rounded p-3 text-[10px] text-white uppercase outline-none focus:border-yellow-500" required><button class="w-full bg-yellow-600 text-black font-bold py-3 rounded text-xs uppercase hover:bg-yellow-500 mt-4">Enviar Reporte</button></form></div>""", True)

@app.route('/completar', methods=['POST'])
def completar():
    supabase.table("pedidos").update({"nombres": request.form['nom'], "dni": request.form['dni'], "imei": request.form['imei'], "c_bloq": request.form['cb'], "operador_tel": request.form['ope'], "plan": request.form['plan'], "equipo": request.form['equipo'], "estado": "EXITOSO"}).eq("id_pedido", request.form['id']).execute()
    return redirect('/gestion')

@app.route('/planes')
def planes():
    precios = [("01 CRÉDITO", "S/15.00"), ("04 CRÉDITOS", "S/60.00"), ("06 CRÉDITOS", "S/90.00"), ("10 CRÉDITOS", "S/150.00"), ("12 CRÉDITOS", "S/120.00"), ("20 CRÉDITOS", "S/200.00")]
    cards = "".join([f'<div class="neon-card p-4 mb-3 border-l-4 border-red-600 flex justify-between items-center"><div><p class="text-sm font-bold text-white uppercase">{p[0]}</p><p class="text-xs text-gray-500">{p[1]}</p></div><a href="https://t.me/jhorny18" target="_blank" class="bg-red-900/20 text-red-500 text-[9px] font-bold px-3 py-2 rounded border border-red-900 uppercase">Comprar</a></div>' for p in precios])
    return layout(f"<h2 class='text-center text-[10px] text-red-500 font-bold mt-10 mb-6 uppercase tracking-widest'>Paquetes Oficiales</h2>{cards}", True)

@app.route('/bloqueo')
def bloqueo():
    return layout(f"""<div class="neon-card p-6 mt-10 text-center"><h2 class="text-[10px] text-red-400 font-bold mb-6 uppercase italic tracking-widest">Solicitar Bloqueo</h2><form action="/solicitar" method="POST"><input type="text" name="num" placeholder="NÚMERO A BLOQUEAR" class="w-full bg-[#0d0d0d] border border-gray-800 rounded-lg p-4 text-center text-lg text-white mb-4 outline-none focus:border-red-500 tracking-widest" required><p class="text-[8px] text-gray-500 mb-4 uppercase">Coste: 1 Crédito / Tiempo: 10-30 min</p><button class="w-full bg-red-600 text-white font-bold py-3 rounded-lg text-sm uppercase shadow-lg shadow-red-600/20 hover:bg-red-500 transition">Procesar Solicitud</button></form></div>""", True)

@app.route('/solicitar', methods=['POST'])
def solicitar():
    if 'user' in session:
        u = session['user']
        res = supabase.table("usuarios").select("creditos").eq("user", u).execute()
        if res.data and res.data[0]['creditos'] > 0:
            supabase.table("usuarios").update({"creditos": res.data[0]['creditos'] - 1}).eq("user", u).execute()
            supabase.table("pedidos").insert({"cliente": u, "numero": request.form['num'], "estado": 'PENDIENTE'}).execute()
    return redirect('/')

@app.route('/soporte')
def soporte():
    return layout(f"""<div class="neon-card p-8 mt-10 text-center border-t-2 border-green-500"><h2 class="text-xl font-bold mb-2 uppercase italic text-white">Soporte 24/7</h2><a href="https://t.me/jhorny18" class="text-green-400 text-sm font-bold block mb-4">@jhorny18</a><p class="text-[9px] text-gray-500 uppercase">Para recargas, reportes de fallos o dudas.</p></div>""", True)

@app.route('/logout')
def logout(): session.clear(); return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
