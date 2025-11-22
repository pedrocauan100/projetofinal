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
                    print("DEBUG: Redirecionando para admin")
                    return redirect(url_for('admin'))
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

@app.route('/admin')
def admin():
    print(f"DEBUG: Acessando /admin - Session: {dict(session)}")
    
    if 'usuario' not in session:
        print("DEBUG: Usuário não está na session - redirecionando para login")
        flash('Acesso não autorizado. Faça login como administrador.', 'error')
        return redirect(url_for('login'))
    
    if session.get('tipo') != 'admin':
        print(f"DEBUG: Tipo de usuário não é admin - Tipo: '{session.get('tipo')}'")
        flash('Acesso não autorizado. Faça login como administrador.', 'error')
        return redirect(url_for('login'))
    
    print("DEBUG: Renderizando admin.html")
    return render_template('admin.html')

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
    if 'usuario' not in session:
        flash('Acesso não autorizado. Faça login como administrador.', 'error')
        return redirect(url_for('login'))
    
    if session.get('tipo') != 'admin':
        flash('Acesso não autorizado. Faça login como administrador.', 'error')
        return redirect(url_for('login'))

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

    return render_template('cadastrarproduto.html')

@app.route('/admin/produtos')
def listar_produtos_admin():
    if 'usuario' not in session:
        flash('Acesso não autorizado. Faça login como administrador.', 'error')
        return redirect(url_for('login'))
    
    if session.get('tipo') != 'admin':
        flash('Acesso não autorizado. Faça login como administrador.', 'error')
        return redirect(url_for('login'))

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM produtos ORDER BY id DESC")
    produtos = cursor.fetchall()
    
    for produto in produtos:
        cursor.execute("""
            SELECT * FROM comentarios 
            WHERE produto_id = %s 
            ORDER BY data_criacao DESC
        """, (produto['id'],))
        comentarios = cursor.fetchall()
        
        # Formatar datas dos comentários
        for comentario in comentarios:
            if comentario['data_criacao']:
                comentario['data_formatada'] = comentario['data_criacao'].strftime('%d/%m/%Y às %H:%M')
            else:
                comentario['data_formatada'] = 'Data não disponível'
        
        produto['comentarios'] = comentarios
        produto['total_comentarios'] = len(comentarios) 
    
    cursor.close()
    conexao.close()

    return render_template('listarprodutos.html', produtos=produtos)

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

    if produto is None:
        cursor.close()
        conexao.close()
        return "Produto não encontrado", 404

    cursor.execute("""
        SELECT c.*, DATE_FORMAT(c.data_criacao, '%d/%m/%Y %H:%i') as data_formatada
        FROM comentarios c 
        WHERE c.produto_id = %s 
        ORDER BY c.data_criacao DESC
    """, (id,))
    comentarios = cursor.fetchall()
    
    cursor.close()
    conexao.close()

    return render_template('paginacompra.html', produto=produto, comentarios=comentarios)

@app.route('/produto/<int:id>/comentario', methods=['POST'])
def adicionar_comentario(id):
    if 'usuario' not in session:
        flash('Faça login para comentar.', 'error')
        return redirect(url_for('login'))
    
    comentario_texto = request.form['comentario']
    
    if not comentario_texto.strip():
        flash('Comentário não pode estar vazio.', 'error')
        return redirect(url_for('pagina_compra', id=id))
    
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO comentarios (produto_id, usuario_email, usuario_nome, comentario)
            VALUES (%s, %s, %s, %s)
        """, (id, session['usuario'], session['nome'], comentario_texto))
        conexao.commit()
        flash('Comentário adicionado com sucesso!', 'success')
    except Exception as e:
        print(f"DEBUG: Erro ao adicionar comentário: {e}")
        flash('Erro ao adicionar comentário.', 'error')
    finally:
        cursor.close()
        conexao.close()
    
    return redirect(url_for('pagina_compra', id=id))

@app.route('/comentario/<int:id>/excluir', methods=['POST'])
def excluir_comentario(id):
    if 'usuario' not in session:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('login'))
    
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT c.*, p.nome as produto_nome 
            FROM comentarios c 
            JOIN produtos p ON c.produto_id = p.id 
            WHERE c.id = %s
        """, (id,))
        comentario = cursor.fetchone()
        
        if comentario:
            if comentario['usuario_email'] == session['usuario'] or session.get('tipo') == 'admin':
                cursor.execute("DELETE FROM comentarios WHERE id = %s", (id,))
                conexao.commit()
                flash('Comentário excluído com sucesso!', 'success')
            else:
                flash('Acesso não autorizado para excluir este comentário.', 'error')
        else:
            flash('Comentário não encontrado.', 'error')
            
    except Exception as e:
        print(f"DEBUG: Erro ao excluir comentário: {e}")
        flash('Erro ao excluir comentário.', 'error')
    finally:
        cursor.close()
        conexao.close()
    
    if comentario:
        return redirect(url_for('pagina_compra', id=comentario['produto_id']))
    else:
        return redirect(url_for('produtos'))

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

    return redirect(url_for('listar_produtos_admin'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Login realizado com sucesso!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)