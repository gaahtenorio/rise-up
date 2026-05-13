# Sistema DISEC — Gestão Nacional de Agências

## Sobre o Projeto

O **Sistema DISEC** é uma aplicação web desenvolvida em **Python + Flask** para gerenciamento nacional de agências bancárias, permitindo controle operacional, ambiental e documental das unidades.

O sistema oferece:

- Cadastro e gestão de agências
- Dashboard estratégico com indicadores
- Controle de usuários e permissões
- Upload de arquivos DWG
- Gestão de vistorias do Corpo de Bombeiros
- Controle de horários de atendimento
- Indicadores ESG e eficiência energética
- APIs REST para integração

---

# Tecnologias Utilizadas

- Python 3
- Flask
- Flask SQLAlchemy
- SQLite
- Jinja2
- HTML5
- CSS3
- JavaScript
- Google Maps API

---

# Estrutura do Projeto

```bash
.
├── app.py
├── data/
│   └── agencias.json
├── uploads/
│   ├── dwg/
│   └── bombeiros/
├── templates/
├── static/
├── disec.db
└── requirements.txt
```

---

# Funcionalidades

## Autenticação e Controle de Acesso

O sistema possui autenticação baseada em sessão:

- Login/logout
- Controle de permissões:
  - Gestão
  - Consulta

Rotas protegidas com:

```python
@login_required
@gestao_required
```

---

## Gestão de Agências

Cada agência possui:

- Prefixo
- Nome
- Município
- UF
- Endereço completo
- Segmento
- Status operacional
- Coordenadas geográficas
- Indicadores ambientais
- Dados BACEN

---

## Indicadores ESG

O sistema monitora:

- Consumo de energia
- Consumo de água
- Resíduos sólidos
- Acessibilidade
- Emissão de carbono
- Eficiência energética
- Índice IDI

### Fórmula de eficiência energética

```text
Eficiência = Consumo de Energia / Área Útil
```

---

## Dashboard Estratégico

O dashboard apresenta:

- Total de agências
- Agências operando
- Agências fechadas
- Agências em reforma
- Média de IDI
- Ranking de eficiência energética
- Distribuição BACEN
- Percentual de acessibilidade
- Indicadores ambientais

---

## Upload de Arquivos DWG

O sistema permite:

- Upload de arquivos `.dwg`
- Download de arquivos
- Exclusão de documentos
- Controle por agência

### Limitações

- Apenas arquivos `.dwg`
- Limite de 50 MB

---

## Gestão de Vistorias dos Bombeiros

Recursos disponíveis:

- Cadastro de protocolo
- Controle de validade
- Upload de PDF
- Download de documentos
- Verificação automática de vencimento

### Limitações

- Apenas PDF
- Limite de 20 MB

---

## Gestão de Usuários

Administradores podem:

- Criar usuários
- Editar usuários
- Alterar permissões
- Ativar/desativar contas
- Excluir usuários

---

# Modelos do Banco de Dados

## Usuario

Responsável pela autenticação e controle de acesso.

## Agencia

Entidade principal do sistema.

## ArquivoDWG

Armazena arquivos técnicos das agências.

## HorarioSAA

Controla horários de atendimento.

## VistoriaBombeiros

Gerencia documentos e vencimentos das vistorias.

## ConfiguracaoSistema

Armazena parâmetros globais do sistema.

---

# API REST

## Agências

| Método | Endpoint |
|---|---|
| GET | `/api/agencias` |
| POST | `/api/agencias` |
| PUT | `/api/agencias/<id>` |
| DELETE | `/api/agencias/<id>` |

---

## Usuários

| Método | Endpoint |
|---|---|
| GET | `/api/usuarios` |
| POST | `/api/usuarios` |
| PUT | `/api/usuarios/<id>` |
| DELETE | `/api/usuarios/<id>` |

---

## DWG

| Método | Endpoint |
|---|---|
| GET | `/api/agencias/<id>/dwg` |
| POST | `/api/agencias/<id>/dwg` |
| DELETE | `/api/agencias/<id>/dwg/<id>` |

---

## Bombeiros

| Método | Endpoint |
|---|---|
| GET | `/api/agencias/<id>/vistoria` |
| POST | `/api/agencias/<id>/vistoria` |
| POST | `/api/agencias/<id>/vistoria/upload` |

---

# Instalação

## 1️ - Clone o projeto

```bash
git clone https://github.com/seu-usuario/disec.git
cd disec
```

---

## 2️ - Crie o ambiente virtual

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3️ - Instale as dependências

```bash
pip install -r requirements.txt
```

---

## 4️ - Configure as variáveis de ambiente

```env
SECRET_KEY=sua_chave_secreta
FLASK_DEBUG=True
GOOGLE_MAPS_API_KEY=sua_api_key
DATABASE_URL=sqlite:///disec.db
```

---

## 5️ - Execute o sistema

```bash
python app.py
```
---

## 🔐 Credenciais iniciais
| Usuário | Senha | Nível |
|--------|------|------|
| visitante | abc | Consulta |

---

# Regras de Negócio

## IDI

O IDI deve estar entre:

```text
1.0 <= IDI <= 10.0
```

---

## CNPJ

Formato obrigatório:

```text
XX.XXX.XXX/XXXX-XX
```

---

# Segurança

- Senhas armazenadas com hash (`werkzeug.security`)
- Controle de sessão
- Upload com validação
- Proteção por níveis de acesso
- Sanitização de nomes de arquivos

---

# Melhorias Futuras

- Integração com PostgreSQL
- Docker
- JWT Authentication
- Logs de auditoria
- Integração com Power BI
- Relatórios em PDF
- Notificações automáticas
- API documentada com Swagger

---

# Autor

**Igor Barbosa**

Sistema desenvolvido para gestão estratégica e operacional de agências bancárias.

---

# Licença

Este projeto é destinado para uso interno e educacional.
