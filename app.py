import os
import json
from functools import wraps
from flask import Flask, render_template, redirect, url_for, session, request, abort
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'fallback_inseguro_troque_em_producao')

# ---------------------------------------------------------------------------
# Usuários com senhas hasheadas
# Em produção, isso deve vir de um banco de dados.
# ---------------------------------------------------------------------------
USUARIOS = {
    "igor.barbosa": {
        "senha_hash": generate_password_hash("123"),
        "nome": "Igor Barbosa",
        "nivel": "Gestão"
    },
    "visitante": {
        "senha_hash": generate_password_hash("abc"),
        "nome": "Usuário Visitante",
        "nivel": "Consulta"
    }
}


# ---------------------------------------------------------------------------
# Decorators de autenticação e autorização
# ---------------------------------------------------------------------------

def login_required(f):
    """Redireciona para login se o usuário não estiver autenticado."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_name' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def gestao_required(f):
    """Retorna 403 se o usuário não tiver nível de Gestão."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_name' not in session:
            return redirect(url_for('login'))
        if session.get('user_level') != 'Gestão':
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_agencias():
    """Carrega as agências do arquivo JSON."""
    json_path = os.path.join(app.root_path, 'data', 'agencias.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_agencia_por_prefixo(prefixo):
    """Busca uma agência pelo prefixo. Retorna None se não encontrar."""
    agencias = get_agencias()
    for ag in agencias:
        if str(ag.get('prefixo')) == str(prefixo):
            return ag
    return None


def get_template_context():
    """Retorna o contexto padrão de sessão para os templates."""
    return {
        'user_level': session.get('user_level'),
        'user_name': session.get('user_name'),
    }


# ---------------------------------------------------------------------------
# Rotas de autenticação
# ---------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_name' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        usuario_input = request.form.get('username', '').strip()
        senha_input = request.form.get('password', '')

        user = USUARIOS.get(usuario_input)

        if user and check_password_hash(user['senha_hash'], senha_input):
            session.clear()
            session['user_name'] = user['nome']
            session['user_level'] = user['nivel']
            return redirect(url_for('index'))

        return render_template('login.html', erro=True)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# Rotas principais
# ---------------------------------------------------------------------------

@app.route('/')
@login_required
def index():
    ctx = get_template_context()
    ctx['page_title'] = 'Página Inicial'
    return render_template('index.html', **ctx)


@app.route('/agencias')
@login_required
def agencias():
    ctx = get_template_context()
    ctx['page_title'] = 'Consulta Nacional de Agências'
    ctx['google_maps_key'] = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('agencias.html', **ctx)


@app.route('/detalhes/<prefixo>')
@login_required
def detalhes(prefixo):
    agencia = get_agencia_por_prefixo(prefixo)

    if agencia is None:
        abort(404)

    # Normaliza campos opcionais para o template
    agencia.setdefault('cidade', agencia.get('municipio', 'N/D'))
    agencia.setdefault('estado', agencia.get('uf', 'N/D'))
    agencia.setdefault('endereco',
        f"{agencia.get('logradouro', '')}, {agencia.get('numero', '')} - "
        f"{agencia.get('bairro', '')}, {agencia.get('municipio', '')} - {agencia.get('uf', '')}"
    )

    ctx = get_template_context()
    ctx['page_title'] = f"Agência {prefixo} - Engenharia"
    ctx['agencia'] = agencia
    return render_template('detalhes.html', **ctx)


@app.route('/dashboard')
@login_required
def dashboard():
    stats_dashboard = {
        'em_reforma': 15,
        'consumo_energia': '1.240 kWh',
        'consumo_agua': '42 m³',
        'carbono_status': '94%'
    }
    ctx = get_template_context()
    ctx['page_title'] = 'Dashboard Estratégico DISEC'
    ctx['stats'] = stats_dashboard
    ctx['google_maps_key'] = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('dashboard.html', **ctx)


@app.route('/admin')
@gestao_required
def admin():
    stats = {
        'em_reforma': 15,
        'consumo_energia': 1240,
        'consumo_agua': 42,
        'carbono': 94
    }
    ctx = get_template_context()
    ctx['page_title'] = 'Gestão DISEC'
    ctx['stats'] = stats
    return render_template('admin.html', **ctx)


# ---------------------------------------------------------------------------
# API interna — dados das agências para o frontend
# ---------------------------------------------------------------------------

@app.route('/api/agencias')
@login_required
def api_agencias():
    """Endpoint JSON para o frontend consumir os dados das agências."""
    from flask import jsonify
    filtro = request.args.get('q', '').strip().lower()
    uf = request.args.get('uf', '').strip().upper()

    agencias = get_agencias()

    if filtro:
        agencias = [
            ag for ag in agencias
            if filtro in ag.get('municipio', '').lower()
            or filtro in ag.get('nome', '').lower()
            or filtro in str(ag.get('prefixo', ''))
        ]

    if uf:
        agencias = [ag for ag in agencias if ag.get('uf', '').upper() == uf]

    return jsonify(agencias)


# ---------------------------------------------------------------------------
# Tratamento de erros
# ---------------------------------------------------------------------------

@app.errorhandler(403)
def forbidden(e):
    ctx = get_template_context()
    return render_template('errors/403.html', **ctx), 403


@app.errorhandler(404)
def not_found(e):
    ctx = get_template_context()
    return render_template('errors/404.html', **ctx), 404


@app.errorhandler(500)
def server_error(e):
    ctx = get_template_context()
    return render_template('errors/500.html', **ctx), 500


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
