import os
import json
from functools import wraps
from flask import (Flask, render_template, redirect, url_for,
                   session, request, abort, jsonify, flash)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ---------------------------------------------------------------------------
# App & DB
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_inseguro_troque_em_producao')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///' + os.path.join(BASE_DIR, 'disec.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------
class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    nome       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    nivel      = db.Column(db.String(20),  nullable=False, default='Consulta')
    ativo      = db.Column(db.Boolean, default=True)
    criado_em  = db.Column(db.DateTime, default=datetime.utcnow)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def to_dict(self):
        return {
            'id':        self.id,
            'username':  self.username,
            'nome':      self.nome,
            'email':     self.email,
            'nivel':     self.nivel,
            'ativo':     self.ativo,
            'criado_em': self.criado_em.strftime('%d/%m/%Y') if self.criado_em else ''
        }


class Agencia(db.Model):
    __tablename__ = 'agencias'

    id         = db.Column(db.Integer, primary_key=True)
    prefixo    = db.Column(db.String(10),  unique=True, nullable=False)
    nome       = db.Column(db.String(150), nullable=False)
    municipio  = db.Column(db.String(100), nullable=False)
    uf         = db.Column(db.String(2),   nullable=False)
    logradouro = db.Column(db.String(200), nullable=True)
    numero     = db.Column(db.String(20),  nullable=True)
    bairro     = db.Column(db.String(100), nullable=True)
    cep        = db.Column(db.String(10),  nullable=True)
    telefone   = db.Column(db.String(20),  nullable=True)
    gerente    = db.Column(db.String(120), nullable=True)
    segmento   = db.Column(db.String(50),  nullable=True, default='Varejo')
    status     = db.Column(db.String(50),  nullable=True, default='Operação Normal')
    lat        = db.Column(db.Float, nullable=True)
    lng        = db.Column(db.Float, nullable=True)
    # ESG
    consumo_energia = db.Column(db.Float, nullable=True)
    consumo_agua    = db.Column(db.Float, nullable=True)
    carbono         = db.Column(db.Float, nullable=True)
    acessibilidade  = db.Column(db.Boolean, default=True)
    criado_em       = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def endereco(self):
        partes = [self.logradouro or '', self.numero or '']
        partes = [p for p in partes if p]
        linha1 = ', '.join(partes)
        linha2 = f"{self.bairro or ''}, {self.municipio} - {self.uf}".strip(', ')
        return f"{linha1} - {linha2}" if linha1 else linha2

    def to_dict(self):
        return {
            'id':               self.id,
            'prefixo':          self.prefixo,
            'nome':             self.nome,
            'municipio':        self.municipio,
            'uf':               self.uf,
            'logradouro':       self.logradouro or '',
            'numero':           self.numero or '',
            'bairro':           self.bairro or '',
            'cep':              self.cep or '',
            'telefone':         self.telefone or '',
            'gerente':          self.gerente or '',
            'segmento':         self.segmento or 'Varejo',
            'status':           self.status or 'Operação Normal',
            'lat':              self.lat,
            'lng':              self.lng,
            'consumo_energia':  self.consumo_energia,
            'consumo_agua':     self.consumo_agua,
            'carbono':          self.carbono,
            'acessibilidade':   self.acessibilidade,
            'endereco':         self.endereco,
            'cidade':           self.municipio,
            'estado':           self.uf,
        }


# ---------------------------------------------------------------------------
# Seed inicial
# ---------------------------------------------------------------------------
def seed_db():
    """Popula o banco com dados iniciais se estiver vazio."""
    if Usuario.query.count() == 0:
        admin = Usuario(
            username='igor.barbosa',
            nome='Igor Barbosa',
            email='igor@bb.com.br',
            nivel='Gestão',
            ativo=True
        )
        admin.set_senha('123')

        visitante = Usuario(
            username='visitante',
            nome='Usuário Visitante',
            email='visitante@bb.com.br',
            nivel='Consulta',
            ativo=True
        )
        visitante.set_senha('abc')

        db.session.add_all([admin, visitante])
        db.session.commit()

    if Agencia.query.count() == 0:
        json_path = os.path.join(BASE_DIR, 'data', 'agencias.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                agencias_json = json.load(f)
            for ag in agencias_json:
                agencia = Agencia(
                    prefixo=str(ag.get('prefixo', '')),
                    nome=ag.get('nome', ''),
                    municipio=ag.get('municipio', ''),
                    uf=ag.get('uf', ''),
                    logradouro=ag.get('logradouro'),
                    numero=ag.get('numero'),
                    bairro=ag.get('bairro'),
                    cep=ag.get('cep'),
                    telefone=ag.get('telefone'),
                    gerente=ag.get('gerente'),
                    segmento=ag.get('segmento', 'Varejo'),
                    status=ag.get('status', 'Operação Normal'),
                    acessibilidade=ag.get('acessibilidade', True),
                    lat=ag.get('lat'),
                    lng=ag.get('lng'),
                    consumo_energia=ag.get('consumo_energia'),
                    consumo_agua=ag.get('consumo_agua'),
                    carbono=ag.get('carbono'),
                )
                db.session.add(agencia)
            db.session.commit()
        except (FileNotFoundError, json.JSONDecodeError):
            pass


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def gestao_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('user_level') != 'Gestão':
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_template_context():
    return {
        'user_level': session.get('user_level'),
        'user_name':  session.get('user_name'),
    }


def get_stats():
    total      = Agencia.query.count()
    em_reforma = Agencia.query.filter_by(status='Em Reforma').count()
    return {
        'total':      total,
        'em_reforma': em_reforma,
    }


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        senha    = request.form.get('password', '')

        user = Usuario.query.filter_by(username=username, ativo=True).first()

        if user and user.check_senha(senha):
            session.clear()
            session['user_id']    = user.id
            session['user_name']  = user.nome
            session['user_level'] = user.nivel
            return redirect(url_for('index'))

        return render_template('login.html', erro=True)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# Páginas principais
# ---------------------------------------------------------------------------
@app.route('/')
@login_required
def index():
    ctx = get_template_context()
    ctx['page_title'] = 'Página Inicial'
    stats = get_stats()
    ctx['total_agencias'] = stats['total']
    ctx['em_reforma']     = stats['em_reforma']
    return render_template('index.html', **ctx)


@app.route('/agencias')
@login_required
def agencias():
    ctx = get_template_context()
    ctx['page_title']       = 'Consulta Nacional de Agências'
    ctx['google_maps_key']  = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('agencias.html', **ctx)


@app.route('/detalhes')
@login_required
def detalhes_index():
    """Redireciona para a primeira agência cadastrada."""
    ag = Agencia.query.order_by(Agencia.nome).first()
    if ag:
        return redirect(url_for('detalhes', prefixo=ag.prefixo))
    abort(404)


@app.route('/detalhes/<prefixo>')
@login_required
def detalhes(prefixo):
    agencia = Agencia.query.filter_by(prefixo=prefixo).first_or_404()
    ctx = get_template_context()
    ctx['page_title']      = f"Agência {prefixo}"
    ctx['agencia']         = agencia
    ctx['google_maps_key'] = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('detalhes.html', **ctx)


@app.route('/dashboard')
@login_required
def dashboard():
    stats = get_stats()
    ctx = get_template_context()
    ctx['page_title']      = 'Dashboard Estratégico DISEC'
    ctx['stats']           = stats
    ctx['google_maps_key'] = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('dashboard.html', **ctx)


@app.route('/admin')
@gestao_required
def admin():
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    ctx = get_template_context()
    ctx['page_title'] = 'Gestão DISEC'
    ctx['usuarios']   = usuarios
    return render_template('admin.html', **ctx)


# ---------------------------------------------------------------------------
# API — Agências
# ---------------------------------------------------------------------------
@app.route('/api/agencias')
@login_required
def api_agencias():
    filtro = request.args.get('q', '').strip().lower()
    uf     = request.args.get('uf', '').strip().upper()

    query = Agencia.query

    if filtro:
        query = query.filter(
            db.or_(
                Agencia.nome.ilike(f'%{filtro}%'),
                Agencia.municipio.ilike(f'%{filtro}%'),
                Agencia.prefixo.ilike(f'%{filtro}%'),
                Agencia.bairro.ilike(f'%{filtro}%'),
            )
        )
    if uf:
        query = query.filter_by(uf=uf)

    agencias = query.order_by(Agencia.nome).all()
    return jsonify([ag.to_dict() for ag in agencias])


@app.route('/api/agencias/<int:agencia_id>', methods=['GET'])
@login_required
def api_agencia_get(agencia_id):
    ag = Agencia.query.get_or_404(agencia_id)
    return jsonify(ag.to_dict())


@app.route('/api/agencias', methods=['POST'])
@gestao_required
def api_agencias_criar():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'erro': 'Dados inválidos'}), 400

    prefixo = str(data.get('prefixo', '')).strip()
    nome    = str(data.get('nome', '')).strip()
    municipio = str(data.get('municipio', '')).strip()
    uf      = str(data.get('uf', '')).strip().upper()

    if not all([prefixo, nome, municipio, uf]):
        return jsonify({'erro': 'Prefixo, nome, município e UF são obrigatórios'}), 400

    if Agencia.query.filter_by(prefixo=prefixo).first():
        return jsonify({'erro': f'Prefixo {prefixo} já cadastrado'}), 409

    ag = Agencia(
        prefixo=prefixo, nome=nome, municipio=municipio, uf=uf,
        logradouro=data.get('logradouro'), numero=data.get('numero'),
        bairro=data.get('bairro'), cep=data.get('cep'),
        telefone=data.get('telefone'), gerente=data.get('gerente'),
        segmento=data.get('segmento', 'Varejo'),
        status=data.get('status', 'Operação Normal'),
        lat=data.get('lat') or None, lng=data.get('lng') or None,
        consumo_energia=data.get('consumo_energia') or None,
        consumo_agua=data.get('consumo_agua') or None,
        carbono=data.get('carbono') or None,
        acessibilidade=bool(data.get('acessibilidade', True)),
    )
    db.session.add(ag)
    db.session.commit()
    return jsonify(ag.to_dict()), 201


@app.route('/api/agencias/<int:agencia_id>', methods=['PUT'])
@gestao_required
def api_agencias_editar(agencia_id):
    ag   = Agencia.query.get_or_404(agencia_id)
    data = request.get_json(force=True)
    if not data:
        return jsonify({'erro': 'Dados inválidos'}), 400

    campos_str = ['nome', 'municipio', 'logradouro', 'numero', 'bairro',
                  'cep', 'telefone', 'gerente', 'segmento', 'status']
    for campo in campos_str:
        if campo in data:
            setattr(ag, campo, str(data[campo]).strip() or None)

    if 'uf' in data:
        ag.uf = str(data['uf']).strip().upper()
    if 'lat' in data:
        ag.lat = float(data['lat']) if data['lat'] not in (None, '') else None
    if 'lng' in data:
        ag.lng = float(data['lng']) if data['lng'] not in (None, '') else None
    if 'consumo_energia' in data:
        ag.consumo_energia = float(data['consumo_energia']) if data['consumo_energia'] not in (None, '') else None
    if 'consumo_agua' in data:
        ag.consumo_agua = float(data['consumo_agua']) if data['consumo_agua'] not in (None, '') else None
    if 'carbono' in data:
        ag.carbono = float(data['carbono']) if data['carbono'] not in (None, '') else None
    if 'acessibilidade' in data:
        ag.acessibilidade = bool(data['acessibilidade'])

    ag.atualizado_em = datetime.utcnow()
    db.session.commit()
    return jsonify(ag.to_dict())


@app.route('/api/agencias/<int:agencia_id>', methods=['DELETE'])
@gestao_required
def api_agencias_deletar(agencia_id):
    ag = Agencia.query.get_or_404(agencia_id)
    db.session.delete(ag)
    db.session.commit()
    return jsonify({'ok': True})


# ---------------------------------------------------------------------------
# API — Usuários
# ---------------------------------------------------------------------------
@app.route('/api/usuarios')
@gestao_required
def api_usuarios():
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return jsonify([u.to_dict() for u in usuarios])


@app.route('/api/usuarios', methods=['POST'])
@gestao_required
def api_usuarios_criar():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'erro': 'Dados inválidos'}), 400

    username = str(data.get('username', '')).strip()
    nome     = str(data.get('nome', '')).strip()
    email    = str(data.get('email', '')).strip()
    senha    = str(data.get('senha', '')).strip()
    nivel    = str(data.get('nivel', 'Consulta')).strip()

    if not all([username, nome, email, senha]):
        return jsonify({'erro': 'Username, nome, e-mail e senha são obrigatórios'}), 400

    if Usuario.query.filter_by(username=username).first():
        return jsonify({'erro': f'Username "{username}" já existe'}), 409
    if Usuario.query.filter_by(email=email).first():
        return jsonify({'erro': f'E-mail "{email}" já cadastrado'}), 409

    u = Usuario(username=username, nome=nome, email=email, nivel=nivel, ativo=True)
    u.set_senha(senha)
    db.session.add(u)
    db.session.commit()
    return jsonify(u.to_dict()), 201


@app.route('/api/usuarios/<int:usuario_id>', methods=['PUT'])
@gestao_required
def api_usuarios_editar(usuario_id):
    u    = Usuario.query.get_or_404(usuario_id)
    data = request.get_json(force=True)
    if not data:
        return jsonify({'erro': 'Dados inválidos'}), 400

    if 'nome' in data:
        u.nome = str(data['nome']).strip()
    if 'email' in data:
        email = str(data['email']).strip()
        existente = Usuario.query.filter_by(email=email).first()
        if existente and existente.id != u.id:
            return jsonify({'erro': 'E-mail já em uso'}), 409
        u.email = email
    if 'nivel' in data:
        u.nivel = str(data['nivel']).strip()
    if 'ativo' in data:
        u.ativo = bool(data['ativo'])
    if 'senha' in data and data['senha']:
        u.set_senha(str(data['senha']))

    db.session.commit()
    return jsonify(u.to_dict())


@app.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
@gestao_required
def api_usuarios_deletar(usuario_id):
    u = Usuario.query.get_or_404(usuario_id)
    if u.id == session.get('user_id'):
        return jsonify({'erro': 'Você não pode excluir sua própria conta'}), 400
    db.session.delete(u)
    db.session.commit()
    return jsonify({'ok': True})


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
# Inicialização
# ---------------------------------------------------------------------------
with app.app_context():
    db.create_all()
    seed_db()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
