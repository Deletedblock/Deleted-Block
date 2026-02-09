import os, random
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
def layout(content, show_nav=False):
    u, r = session.get('user'), session.get('rol')
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
        function closeReport() { document.getElementById('modalReport').classList.add('hidden'); }
    </script>
    """
    
    # MODAL HTML (Oculto por defecto)
    modal_html = """
    <div id="modalReport" class="fixed inset-0 bg-black/90 hidden z-50 flex items-center justify-center p-4">
        <div class="neon-card w-full max-w-sm p-6 relative bg-[#0a0a0a]">
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
    return f"""<!DOCTYPE html><html lang="es"><head><script src="https://cdn.tailwindcss.com"></script><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><style>body {{ background-color: #050505; color: white; font-family: sans-serif; touch-action: manipulation; overflow-x: hidden; }}.neon-card {{ background: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 20px; }}.input-dark {{ background: #141414; border: 1px solid #222; border-radius: 12px; padding: 12px; width: 100%; outline: none; color: white; }}</style>{modal_script}</head><body class="min-h-screen p-4 flex flex-col items-center"><div class="w-full max-w-sm">{nav}{content}</div>{modal_html}</body></html>"""

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
            btn = f"""<button onclick="showReport('{p.get('nombres','')}','{p.get('dni','')}','{p.get('imei','')}','{p.get('c_bloq','')}','{p.get('operador_tel','')}','{p.get('plan','')}','{p.get('equipo','')}')" class="bg-red-900/20 text-red-500 border border-red-500/50 px-3 py-1 rounded text-[8px] font-bold">VER REPORTE</button>"""
        else:
            btn = '<span class="text-[8px] text-yellow-500 italic font-bold tracking-widest">PROCESANDO</span>'
        h += f'<div class="flex justify-between items-center border-b border-gray-900 py-3"><div class="flex flex-col"><span class="text-xs font-mono text-white">{p["numero"]}</span><span class="text-[8px] text-gray-500 uppercase">{p["estado"]}</span></div>{btn}</div>'

    return layout(f"""
        <div class="flex flex-col items-center mb-6 mt-4"><div class="w-16 h-16 bg-black rounded-full border-2 border-red-900 flex items-center justify-center mb-2 shadow-2xl shadow-red-900/20"><span class="text-3xl font-bold italic text-red-600">D</span></div><h1 class="text-lg font-bold tracking-widest uppercase">DELETED BLOCK</h1></div>
        <div class="grid grid-cols-2 gap-3 mb-6">
            <div class="neon-card p-4 text-center border-b-4 border-blue-600"><p class="text-[8px] text-gray-500 uppercase font-bold">Usados</p><h2 class="text-2xl font-bold">{usados}</h2></div>
            <div class="neon-card p-4 text-center border-b-4 border-red-600"><p class="text-[8px] text-gray-500 uppercase font-bold">Restantes</p><h2 class="text-2xl font-bold">{rest}</h2></div>
        </div>
        <div class="neon-card p-5"><h3 class="text-[9px] font-bold text-red-400 uppercase mb-4 text-center border-b border-gray-900 pb-2">Historial</h3><div class="space-y-1">{h or "<p class='text-center text-gray-600 text-xs py-4'>Sin historial</p>"}</div></div>
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
    return layout(f"""<div class="flex flex-col items-center mt-12"><div class="w-20 h-20 bg-black rounded-full border-4 border-red-900 flex items-center justify-center mb-4 shadow-2xl"><span class="text-4xl font-bold italic text-white">D</span></div><h1 class="text-xl font-bold mb-1 uppercase tracking-widest text-white">DELETED BLOCK</h1><form method="post" class="w-full space-y-4 mt-4"><input name="u" placeholder="Usuario" class="input-dark"><input name="p" type="password" placeholder="Contraseña" class="input-dark"><div class="flex gap-2"><div class="bg-white text-black p-3 rounded-xl font-mono font-bold w-1/2 text-center text-lg">{session['captcha_val']}</div><input name="cap" placeholder="Captcha" class="input-dark w-1/2 text-center"></div><button class="w-full bg-red-800 p-4 rounded-2xl font-bold text-sm uppercase">Acceder</button></form></div>""", False)

@app.route('/panel_admin', methods=['GET', 'POST'])
def panel_admin():
    u_log, r_log = session.get('user'), session.get('rol')
    if u_log != 'jhorny' and r_log != 'admin': return redirect('/')
    
    if request.method == 'POST':
        action = request.form['action']
        if action == 'crear':
            supabase.table("usuarios").insert({"user": request.form['u'], "pass": request.form['p'], "rol": request.form['r'], "creditos": 0, "creado_por": u_log}).execute()
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
    lista = "".join([f'<div class="flex justify-between text-[10px] p-3 border-b border-gray-900"><span>{u["user"]} ({u["rol"]})</span><span class="text-red-500 font-bold">{u["creditos"]} Cr.</span></div>' for u in users])
    return layout(f"""<div class="neon-card p-6 mt-4"><h2 class="text-[10px] text-red-500 font-bold uppercase text-center mb-6 tracking-widest italic">Panel ({r_log})</h2><form method="POST" class="space-y-3 mb-8"><input type="hidden" name="action" value="crear"><input name="u" placeholder="Usuario" class="input-dark text-xs"><input name="p" placeholder="Pass" class="input-dark text-xs"><select name="r" class="input-dark text-xs bg-[#141414]"><option value="user">Cliente</option>{"<option value='operador'>Operador</option><option value='admin'>Admin</option>" if u_log == 'jhorny' else ""}</select><button class="w-full bg-blue-700 p-3 rounded-xl font-bold text-[9px]">REGISTRAR</button></form><form method="POST" class="space-y-3 mb-8"><input type="hidden" name="action" value="creditos"><input name="target" placeholder="Destino" class="input-dark text-xs"><input name="cant" type="number" placeholder="Cantidad" class="input-dark text-xs"><button class="w-full bg-red-700 p-3 rounded-xl font-bold text-[9px]">CARGAR</button></form><div class="mt-6">{lista}</div></div>""", True)

@app.route('/gestion')
def gestion():
    if session.get('rol') not in ['operador', 'admin'] and session.get('user') != 'jhorny': return redirect('/')
    ps = supabase.table("pedidos").select("id_pedido, cliente, numero").eq("estado", "PENDIENTE").execute().data
    l = "".join([f'<div class="neon-card p-4 mb-3 flex justify-between items-center"><div><p class="text-[7px] text-gray-500 uppercase">CLIENTE: {p["cliente"]}</p><p class="text-lg font-mono text-white">{p["numero"]}</p></div><a href="/trabajar/{p["id_pedido"]}" class="bg-yellow-600 text-black px-4 py-2 rounded-xl text-[10px] font-black uppercase">Agarrar</a></div>' for p in ps])
    return layout(f"<h2 class='text-center text-[10px] text-yellow-500 font-bold mt-10 mb-6 uppercase'>Bandeja Operador</h2>{l or '<p class=\"text-center text-gray-600 text-xs py-10\">Sin pendientes</p>'}", True)

@app.route('/trabajar/<int:id_p>')
def trabajar(id_p):
    p = supabase.table("pedidos").select("*").eq("id_pedido", id_p).execute().data[0]
    return layout(f"""<div class="neon-card p-6 mt-10"><h2 class="text-center text-[10px] text-yellow-500 font-bold mb-6 italic uppercase">Llenar: {p['numero']}</h2><form action="/completar" method="POST" class="space-y-3"><input type="hidden" name="id_p" value="{id_p}"><input name="nom" placeholder="NOMBRES" class="input-dark text-xs" required><input name="dni" placeholder="DNI" class="input-dark text-xs" required><input name="ope" placeholder="OPERADOR" class="input-dark text-xs" required><input name="plan" placeholder="PLAN" class="input-dark text-xs" required><input name="equ" placeholder="EQUIPO" class="input-dark text-xs" required><input name="imei" placeholder="IMEI" class="input-dark text-xs" required><input name="cb" placeholder="C.BLOQ" class="input-dark text-xs" required><button class="w-full bg-green-600 p-4 rounded-xl font-black text-[10px] uppercase">Enviar Reporte</button></form></div>""", True)

@app.route('/completar', methods=['POST'])
def completar():
    supabase.table("pedidos").update({"nombres": request.form['nom'], "dni": request.form['dni'], "imei": request.form['imei'], "c_bloq": request.form['cb'], "operador_tel": request.form['ope'], "plan": request.form['plan'], "equipo": request.form['equ'], "estado": 'EXITOSO'}).eq("id_pedido", request.form['id_p']).execute()
    return redirect('/gestion')

@app.route('/planes')
def planes():
    precios = [("01 CRÉDITO", "S/15.00"), ("04 CRÉDITOS", "S/60.00"), ("06 CRÉDITOS", "S/90.00"), ("10 CRÉDITOS", "S/150.00"), ("12 CRÉDITOS", "S/120.00"), ("20 CRÉDITOS", "S/200.00")]
    cards = "".join([f'<div class="neon-card p-4 mb-3 border-l-4 border-red-600 flex justify-between items-center"><div><p class="text-sm font-bold text-white uppercase">{p[0]}</p><p class="text-[10px] text-gray-500 font-mono">{p[1]}</p></div><a href="https://t.me/Angel_dox1" class="bg-red-600 px-4 py-2 rounded-xl text-[9px] font-bold text-white">Comprar</a></div>' for p in precios])
    return layout(f"<h2 class='text-center text-[10px] text-red-500 font-bold mt-10 mb-6 uppercase tracking-widest'>Paquetes Oficiales</h2>{cards}", True)

@app.route('/bloqueo')
def bloqueo():
    return layout(f"""<div class="neon-card p-6 mt-10 text-center"><h2 class="text-[10px] text-red-400 font-bold mb-6 uppercase italic tracking-widest">Solicitar Bloqueo</h2><form action="/solicitar" method="POST" class="space-y-4"><div class="bg-black p-5 rounded-2xl border border-gray-800"><input type="text" name="num" placeholder="901432132" maxlength="9" class="bg-transparent w-full text-center text-4xl font-mono text-white outline-none" required></div><button class="w-full bg-red-800 p-4 rounded-2xl font-bold text-sm uppercase">Enviar Solicitud</button></form></div>""", True)

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
    return layout(f"""<div class="neon-card p-8 mt-10 text-center border-t-2 border-green-500"><h2 class="text-xl font-bold mb-2 uppercase italic text-white">Soporte 24/7</h2><a href="https://t.me/Angel_dox1" class="inline-block w-full bg-green-600 p-4 rounded-3xl font-bold text-white uppercase text-xs">Ir a Telegram</a></div>""", True)

@app.route('/logout')
def logout(): session.clear(); return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
