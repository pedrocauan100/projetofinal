from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector as my
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'minha_chave_secreta'  

def conectar_banco():
    conexao = my.connect(
        host="localhost",
        user="root",
        password="snoopy10",
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

        print(f"DEBUG: Tentando login com email: '{email}' e senha: '{senha}'")

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conexao.close()

        if usuario:
            print(f"DEBUG: Usuário encontrado!")
            print(f"DEBUG: Email no BD: '{usuario['email']}'")
            print(f"DEBUG: Senha no BD: '{usuario['senha']}'")
            print(f"DEBUG: Tipo no BD: '{usuario['tipo']}'")
            
            if senha == usuario['senha']:
                print("DEBUG: Senha CORRETA!")
                session['usuario'] = usuario['email']
                session['nome'] = usuario['nome']
                session['tipo'] = usuario['tipo']
                
                user_type = usuario['tipo'].strip().lower()
                print(f"DEBUG: Tipo processado: '{user_type}'")
                
                if user_type == 'admin':
                    print("DEBUG: Redirecionando para cadastrar_produto")
                    return redirect(url_for('cadastrar_produto'))
                else:
                    print("DEBUG: Redirecionando para produtos")
                    return redirect(url_for('produtos'))
            else:
                print("DEBUG: Senha INCORRETA!")
                flash('Senha incorreta.', 'error')
                return redirect(url_for('login'))
        else:
            print("DEBUG: E-mail NÃO encontrado no banco!")
            flash('E-mail não encontrado.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html', errou=False)

@app.route('/cadastrar_conta', methods=['GET', 'POST'])
def cadastrar_conta():
    conexao = conectar_banco()
    if not conexao:
        return render_template('cadastrarConta.html', erro="Erro de conexão com o banco de dados.", sucesso=False)
    
    cursor = conexao.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        existente = cursor.fetchone()

        if existente:
            return render_template('cadastrarConta.html', erro="E-mail já cadastrado.", sucesso=False)

        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES (%s, %s, %s, %s)
        """, (nome, email, senha, tipo))
        conexao.commit()

        return render_template('cadastrarConta.html', sucesso=True)

    return render_template('cadastrarConta.html', sucesso=False)

@app.route('/cadastrarproduto', methods=['GET', 'POST'])
def cadastrar_produto():
    print(f"DEBUG: Acessando cadastrar_produto - Session: {dict(session)}")
    
    if 'usuario' not in session:
        print("DEBUG: Usuário não está na session")
        flash('Acesso não autorizado. Faça login como administrador.', 'error')
        return redirect(url_for('login'))
    
    if session.get('tipo') != 'admin':
        print(f"DEBUG: Tipo de usuário não é admin - Tipo: '{session.get('tipo')}'")
        flash('Acesso não autorizado. Faça login como administrador.', 'error')
        return redirect(url_for('login'))

    # Buscar produtos existentes para exibir na lista
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos ORDER BY id DESC")
    produtos = cursor.fetchall()
    cursor.close()
    conexao.close()

    if request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco']
        descricao = request.form['descricao']
        imagem = request.form['imagem']
        tipo = request.form['tipo']
        validade = request.form['validade']

        print(f"DEBUG: Cadastrando produto - Nome: {nome}, Tipo: {tipo}, Validade: {validade}")

        conexao = conectar_banco()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                INSERT INTO produtos (nome, preco, descricao, imagem, tipo, validade)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, preco, descricao, imagem, tipo, validade))
            conexao.commit()
            flash('Produto cadastrado com sucesso!', 'success')
        except Exception as e:
            print(f"DEBUG: Erro ao cadastrar produto: {e}")
            flash(f'Erro ao cadastrar produto: {e}', 'error')
        finally:
            cursor.close()
            conexao.close()

        return redirect(url_for('cadastrar_produto'))

    return render_template('cadastrarproduto.html', produtos=produtos)

@app.route('/produtos')
def produtos():
    if 'usuario' not in session:
        flash('Faça login para acessar os produtos.', 'error')
        return redirect(url_for('login'))

    print(f"DEBUG: Usuário {session['usuario']} acessando produtos")
    
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    cursor.close()
    conexao.close()

    print(f"DEBUG: {len(produtos)} produtos carregados do banco")
    
    for produto in produtos:
        print(f"DEBUG Produto: {produto['nome']} - Imagem: {produto['imagem']}")

    return render_template('produtos.html', produtos=produtos)

@app.route('/produto/<int:id>')
def pagina_compra(id):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE id = %s", (id,))
    produto = cursor.fetchone()
    cursor.close()
    conexao.close()

    if produto is None:
        return "Produto não encontrado", 404

    return render_template('paginacompra.html', produto=produto)

@app.route('/produto/<int:id>/excluir', methods=['POST'])
def excluir_produto(id):
    if 'usuario' not in session:
        flash('Acesso não autorizado. Faça login.', 'error')
        return redirect(url_for('login'))
    
    if session.get('tipo') != 'admin':
        flash('Acesso não autorizado. Apenas administradores podem excluir produtos.', 'error')
        return redirect(url_for('produtos'))

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:
        # Primeiro busca o produto para mostrar o nome no feedback
        cursor.execute("SELECT nome FROM produtos WHERE id = %s", (id,))
        produto = cursor.fetchone()
        
        if produto:
            cursor.execute("DELETE FROM produtos WHERE id = %s", (id,))
            conexao.commit()
            flash(f'Produto "{produto["nome"]}" excluído com sucesso!', 'success')
        else:
            flash('Produto não encontrado.', 'error')
            
    except Exception as e:
        print(f"DEBUG: Erro ao excluir produto: {e}")
        flash('Erro ao excluir produto.', 'error')
    finally:
        cursor.close()
        conexao.close()

    return redirect(url_for('cadastrar_produto'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)