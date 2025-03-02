from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)

# Definir uma chave secreta para usar sessões
app.secret_key = "sua_chave_secreta_aqui"

# Dados de login fixos (pode ser substituído por banco de dados)
usuarios = {
    "jvrs": {"senha": "senha123", "nome": "João Vitor Ribeiro da Silva", "data_nasc": "2004-01-26"},
    "usuario2": {"senha": "senha456", "nome": "Maria", "data_nasc": "1995-05-15"}
}

def calcular_idade(data_nasc):
    try:
        data_nascimento = datetime.strptime(data_nasc, "%Y-%m-%d")
        idade = (datetime.now() - data_nascimento).days // 365
        return idade
    except ValueError:
        return None  # Retorna None se a data for inválida

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        
        # Verifica se o login é válido
        if usuario in usuarios and usuarios[usuario]["senha"] == senha:
            session['usuario'] = usuario  # Armazena o nome do usuário na sessão
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
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if calcular_idade(dataNasc) < 18:
            error = "Idade insuficiente"
        else:
            if usuario in usuarios:
                error = "Usuário já cadastrado!"
            else:
                # Adiciona novo usuário
                usuarios[usuario] = {
                    "senha": senha,
                    "nome": nome,
                    "data_nasc": dataNasc
                }
                session['usuario'] = usuario  # Armazena o usuário na sessão
                return redirect(url_for("dashboard"))

    return render_template("novo_login.html", error=error)

@app.route("/dashboard")
def dashboard():
    if 'usuario' in session:
        usuario = session['usuario']
        nome = usuarios[usuario]["nome"]
        data_nasc = usuarios[usuario]["data_nasc"]
        
        idade = calcular_idade(data_nasc)
        data_nascimento_formatada = datetime.strptime(data_nasc, "%Y-%m-%d").strftime("%d/%m/%Y")
        
        return render_template("dashboard.html", nome=nome, data_nasc=data_nascimento_formatada, idade=idade)
    return redirect(url_for("login"))  # Redireciona para o login caso não haja sessão ativa

@app.route("/logout")
def logout():
    session.pop('usuario', None)  # Remove o usuário da sessão
    return redirect(url_for("login"))  # Redireciona de volta para a página de login

if __name__ == "__main__":
    app.run(debug=True)
