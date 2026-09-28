from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = "techstore-chave-secreta"


# =========================
# BANCO DE DADOS
# =========================

def conectar_banco():

    conexao = sqlite3.connect("loja.db")

    conexao.row_factory = sqlite3.Row

    return conexao


# =========================
# PRODUTOS
# =========================

def buscar_produtos():

    conexao = conectar_banco()

    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM produtos ORDER BY id DESC"
    )

    produtos = cursor.fetchall()

    conexao.close()

    return produtos


def buscar_produto(produto_id):

    conexao = conectar_banco()

    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT *
        FROM produtos
        WHERE id = ?
        """,
        (produto_id,)
    )

    produto = cursor.fetchone()

    conexao.close()

    return produto


# =========================
# CARRINHO
# =========================

def buscar_carrinho():

    carrinho = session.get("carrinho", {})

    if not carrinho:
        return []

    # Converte carrinho antigo para o novo formato
    if isinstance(carrinho, list):

        novo_carrinho = {}

        for produto_id in carrinho:

            produto_id = str(produto_id)

            if produto_id in novo_carrinho:

                novo_carrinho[produto_id] += 1

            else:

                novo_carrinho[produto_id] = 1

        carrinho = novo_carrinho

        session["carrinho"] = carrinho
        session.modified = True


    conexao = conectar_banco()

    cursor = conexao.cursor()

    produtos = []


    for produto_id, quantidade in carrinho.items():

        cursor.execute(
            """
            SELECT *
            FROM produtos
            WHERE id = ?
            """,
            (produto_id,)
        )

        produto = cursor.fetchone()


        if produto:

            produtos.append({

                "produto": produto,

                "quantidade": quantidade,

                "subtotal": produto["preco"] * quantidade

            })


    conexao.close()

    return produtos


# =========================
# ADMINISTRADOR
# =========================

def usuario_admin():

    return session.get("usuario_admin") is True


# =========================
# PÁGINA INICIAL
# =========================

@app.route("/")
def inicio():

    produtos = buscar_produtos()

    return render_template(
        "index.html",
        produtos=produtos
    )


# =========================
# PRODUTOS
# =========================

@app.route("/produtos")
def pagina_produtos():

    produtos = buscar_produtos()

    return render_template(
        "produtos.html",
        produtos=produtos
    )


@app.route("/produto/<int:produto_id>")
def produto(produto_id):

    produto = buscar_produto(produto_id)

    if not produto:

        return "Produto não encontrado", 404


    return render_template(
        "produto.html",
        produto=produto
    )


# =========================
# CARRINHO
# =========================

@app.route("/carrinho")
def carrinho():

    produtos = buscar_carrinho()


    total = sum(
        item["subtotal"]
        for item in produtos
    )


    quantidade_total = sum(
        item["quantidade"]
        for item in produtos
    )


    return render_template(
        "carrinho.html",

        produtos=produtos,

        total=total,

        quantidade_total=quantidade_total
    )


@app.route("/adicionar/<int:produto_id>")
def adicionar_carrinho(produto_id):

    if not buscar_produto(produto_id):

        return "Produto não encontrado", 404


    carrinho = session.get("carrinho", {})


    # Corrige carrinho antigo
    if isinstance(carrinho, list):

        novo_carrinho = {}

        for id_produto in carrinho:

            id_produto = str(id_produto)

            if id_produto in novo_carrinho:

                novo_carrinho[id_produto] += 1

            else:

                novo_carrinho[id_produto] = 1

        carrinho = novo_carrinho


    produto_id = str(produto_id)


    if produto_id in carrinho:

        carrinho[produto_id] += 1

    else:

        carrinho[produto_id] = 1


    session["carrinho"] = carrinho

    session.modified = True


    return redirect("/carrinho")


@app.route("/aumentar/<int:produto_id>")
def aumentar_quantidade(produto_id):

    carrinho = session.get("carrinho", {})


    produto_id = str(produto_id)


    if produto_id in carrinho:

        carrinho[produto_id] += 1


    session["carrinho"] = carrinho

    session.modified = True


    return redirect("/carrinho")


@app.route("/diminuir/<int:produto_id>")
def diminuir_quantidade(produto_id):

    carrinho = session.get("carrinho", {})


    produto_id = str(produto_id)


    if produto_id in carrinho:

        carrinho[produto_id] -= 1


        if carrinho[produto_id] <= 0:

            del carrinho[produto_id]


    session["carrinho"] = carrinho

    session.modified = True


    return redirect("/carrinho")


@app.route("/remover/<int:produto_id>")
def remover_carrinho(produto_id):

    carrinho = session.get("carrinho", {})


    produto_id = str(produto_id)


    if produto_id in carrinho:

        del carrinho[produto_id]


    session["carrinho"] = carrinho

    session.modified = True


    return redirect("/carrinho")


@app.route("/limpar-carrinho")
def limpar_carrinho():

    session["carrinho"] = {}

    return redirect("/carrinho")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        senha = request.form["senha"]


        conexao = conectar_banco()

        cursor = conexao.cursor()


        cursor.execute(
            """
            SELECT *
            FROM usuarios
            WHERE email = ?
            """,
            (email,)
        )


        usuario = cursor.fetchone()


        if usuario:

            senha_correta = False


            try:

                senha_correta = check_password_hash(
                    usuario["senha"],
                    senha
                )

            except ValueError:

                # Compatibilidade com usuários antigos
                senha_correta = (
                    usuario["senha"] == senha
                )


                if senha_correta:

                    nova_senha = generate_password_hash(
                        senha
                    )


                    cursor.execute(
                        """
                        UPDATE usuarios
                        SET senha = ?
                        WHERE id = ?
                        """,
                        (
                            nova_senha,
                            usuario["id"]
                        )
                    )


                    conexao.commit()


            if senha_correta:

                session["usuario_id"] = usuario["id"]

                session["usuario_nome"] = usuario["nome"]

                session["usuario_admin"] = (
                    usuario["email"]
                    == "admin@techstore.com"
                )


                conexao.close()


                return redirect("/")


        conexao.close()


        return render_template(
            "login.html",
            erro="E-mail ou senha incorretos."
        )


    return render_template("login.html")


# =========================
# CADASTRO
# =========================

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form["nome"]

        email = request.form["email"]

        senha = request.form["senha"]


        senha_hash = generate_password_hash(
            senha
        )


        conexao = conectar_banco()

        cursor = conexao.cursor()


        cursor.execute(
            """
            SELECT *
            FROM usuarios
            WHERE email = ?
            """,
            (email,)
        )


        usuario_existente = cursor.fetchone()


        if usuario_existente:

            conexao.close()


            return render_template(
                "cadastro.html",
                erro="Este e-mail já está cadastrado."
            )


        cursor.execute(
            """
            INSERT INTO usuarios
            (nome, email, senha)
            VALUES (?, ?, ?)
            """,
            (
                nome,
                email,
                senha_hash
            )
        )


        conexao.commit()

        conexao.close()


        return redirect("/login")


    return render_template("cadastro.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop("usuario_id", None)

    session.pop("usuario_nome", None)

    session.pop("usuario_admin", None)


    return redirect("/")


# =========================
# CHECKOUT
# =========================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    produtos = buscar_carrinho()


    if not produtos:

        return redirect("/carrinho")


    total = sum(
        item["subtotal"]
        for item in produtos
    )


    if request.method == "POST":

        nome = request.form["nome"]

        endereco = request.form["endereco"]

        pagamento = request.form["pagamento"]


        conexao = conectar_banco()

        cursor = conexao.cursor()


        cursor.execute(
            """
            INSERT INTO pedidos
            (nome, endereco, pagamento, total)
            VALUES (?, ?, ?, ?)
            """,
            (
                nome,
                endereco,
                pagamento,
                total
            )
        )


        pedido_id = cursor.lastrowid


        conexao.commit()

        conexao.close()


        session["carrinho"] = {}


        return render_template(
            "pedido.html",

            pedido_id=pedido_id,

            nome=nome,

            total=total
        )


    return render_template(
        "checkout.html",

        produtos=produtos,

        total=total
    )


# =========================
# ADMIN
# =========================

@app.route("/admin")
def admin():

    if not usuario_admin():

        return redirect("/login")


    produtos = buscar_produtos()


    conexao = conectar_banco()

    cursor = conexao.cursor()


    cursor.execute(
        """
        SELECT *
        FROM pedidos
        ORDER BY id DESC
        """
    )


    pedidos = cursor.fetchall()


    conexao.close()


    return render_template(
        "admin.html",

        produtos=produtos,

        pedidos=pedidos
    )


# =========================
# CADASTRAR PRODUTO
# =========================

@app.route("/admin/produto", methods=["GET", "POST"])
def cadastrar_produto():

    if not usuario_admin():

        return redirect("/login")


    if request.method == "POST":

        nome = request.form["nome"]

        preco = float(
            request.form["preco"]
        )

        categoria = request.form["categoria"]


        conexao = conectar_banco()

        cursor = conexao.cursor()


        cursor.execute(
            """
            INSERT INTO produtos
            (nome, preco, categoria)
            VALUES (?, ?, ?)
            """,
            (
                nome,
                preco,
                categoria
            )
        )


        conexao.commit()

        conexao.close()


        return redirect("/produtos")


    return render_template(
        "cadastrar_produto.html"
    )


# =========================
# INICIAR SISTEMA
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )