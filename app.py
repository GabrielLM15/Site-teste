from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "sua_chave_secreta_aqui"

# Inicialize o SQLAlchemy
db = SQLAlchemy(app)

# Modelo para a tabela de usuários
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(50), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    data_nasc = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<Usuario {self.nome}>"

# Criação do banco de dados (isso só precisa ser feito uma vez)
with app.app_context():
    db.create_all()

def calcular_idade(data_nasc):
    try:
        data_nascimento = datetime.strptime(data_nasc, "%Y-%m-%d")
        idade = (datetime.now() - data_nascimento).days // 365
        return idade
    except ValueError:
        return None 

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        
        # Verificar no banco de dados
        user = Usuario.query.filter_by(email=email).first()
        if user and user.senha == senha:
            session['email'] = email
            return redirect(url_for("dashboard"))
        else:
            error = "Login ou senha inválidos! Tente novamente."
    
    return render_template("login.html", error=error)

@app.route("/novoLogin", methods=["GET", "POST"])
def novoLogin():
    error = None
    if request.method == "POST":
        nome = request.form["nome"]
        dataNasc = request.form["dataNasc"]
        email = request.form["email"]
        senha = request.form["senha"]

        if calcular_idade(dataNasc) < 18:
            error = "Idade insuficiente"
        else:
            # Verificar se o usuário já existe no banco de dados
            user_exists = Usuario.query.filter_by(email=email).first()
            if user_exists:
                error = "Usuário já cadastrado!"
            else:
                novo_email = Usuario(
                    email=email,
                    senha=senha,
                    nome=nome,
                    data_nasc=dataNasc
                )
                db.session.add(novo_email)
                db.session.commit()
                session['email'] = email
                return redirect(url_for("dashboard"))

    return render_template("novo_login.html", error=error)

@app.route("/atualizarCadastro", methods=["GET", "POST"])
def atualizarCadastro():
    error = None
    email_logado = session.get('email')
    
    if not email_logado:
        return redirect(url_for("login"))

    # Buscar dados do usuário no banco de dados
    dados_email = Usuario.query.filter_by(email=email_logado).first()
    if not dados_email:
        return redirect(url_for("login"))

    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]
        
        dados_email.nome = nome
        dados_email.senha = senha
        
        db.session.commit()
        
        return redirect(url_for("dashboard"))

    return render_template("atualizar_cadastro.html", email=dados_email)

@app.route("/dashboard")
def dashboard():
    if 'email' in session:
        email = session['email']
        
        # Buscar dados do usuário no banco de dados
        dados_email = Usuario.query.filter_by(email=email).first()
        if dados_email:
            nome = dados_email.nome
            data_nasc = dados_email.data_nasc
            
            idade = calcular_idade(data_nasc)
            data_nascimento_formatada = datetime.strptime(data_nasc, "%Y-%m-%d").strftime("%d/%m/%Y")
            
            return render_template("dashboard.html", nome=nome, data_nasc=data_nascimento_formatada, idade=idade)
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
