from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector as my
import bcrypt

app = Flask(__name__)
app.secret_key = '12345'

def conectar_banco():
    conexao = my.connect(
        host="localhost",
        user="root",
        password="",
        database="pedrosuperselect"
    )
    return conexao

@app.route('/')
def index():
    titulo = 'Página inicial'
    return render_template('index.html', titulo=titulo)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conexao.close()

        if usuario:
            # Verifica senha com bcrypt
            if bcrypt.checkpw(senha.encode('utf-8'), usuario['senha'].encode('utf-8')):
                session['usuario'] = usuario['email']
                session['nome'] = usuario['nome']
                session['tipo'] = usuario['tipo']

                if usuario['tipo'].strip().lower() == 'admin':
                    return redirect(url_for('cadastrar_produto'))
                else:
                    return redirect(url_for('produtos'))
            else:
                flash('Senha incorreta.', 'error')
                return redirect(url_for('login'))
        else:
            flash('E-mail não encontrado.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html', errou=False)

@app.route('/cadastrar_conta', methods=['GET', 'POST'])
def cadastrar_conta():
    sucesso = False
    erro = None

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        # Verificar se já existe usuário com o mesmo email
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            erro = 'E-mail já cadastrado.'
        else:
            # Hash da senha
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)",
                           (nome, email, senha_hash.decode('utf-8'), tipo))
            conexao.commit()
            sucesso = True

        cursor.close()
        conexao.close()

    return render_template('cadastrarConta.html', sucesso=sucesso, erro=erro)

@app.route('/cadastrarproduto', methods=['GET', 'POST'])
def cadastrar_produto():
    if 'usuario' not in session or session.get('tipo').strip().lower() != 'admin':
        return redirect(url_for('login'))
    # Aqui você coloca a lógica para cadastro de produto
    return "Tela de cadastro de produto - ainda não implementada"

@app.route('/produtos')
def produtos():
    # Exemplo simples para usuários comuns
    return "Tela de listagem de produtos - ainda não implementada"

if __name__ == '__main__':
    app.run(debug=True)
