import sqlite3


conexao = sqlite3.connect("loja.db")

cursor = conexao.cursor()


produtos = [

    ("Mouse Gamer", 149.90, "Periféricos"),

    ("Teclado Mecânico", 249.90, "Periféricos"),

    ("Headset Gamer", 199.90, "Áudio"),

    ("Monitor 24 Polegadas", 899.90, "Monitores"),

    ("Webcam Full HD", 299.90, "Câmeras"),

    ("Mousepad Gamer", 79.90, "Acessórios"),

    ("Teclado Gamer RGB", 179.90, "Periféricos"),

    ("Mouse Wireless", 129.90, "Periféricos"),

    ("Headset Bluetooth", 229.90, "Áudio"),

    ("Monitor Gamer 27 Polegadas", 1299.90, "Monitores"),

    ("Suporte para Monitor", 189.90, "Acessórios"),

    ("Microfone USB", 349.90, "Áudio"),

    ("Webcam 2K", 449.90, "Câmeras"),

    ("Ring Light", 119.90, "Iluminação"),

    ("Hub USB 3.0", 89.90, "Acessórios"),

    ("Adaptador Bluetooth USB", 59.90, "Acessórios"),

    ("SSD 480GB", 299.90, "Armazenamento"),

    ("SSD 1TB", 499.90, "Armazenamento"),

    ("HD Externo 1TB", 379.90, "Armazenamento"),

    ("Memória RAM 8GB", 159.90, "Componentes"),

    ("Memória RAM 16GB", 289.90, "Componentes"),

    ("Placa de Vídeo", 1899.90, "Componentes"),

    ("Fonte 650W", 349.90, "Componentes"),

    ("Gabinete Gamer", 399.90, "Componentes"),

    ("Cooler para Processador", 149.90, "Componentes"),

    ("Cabo HDMI 2.1", 69.90, "Cabos"),

    ("Cabo DisplayPort", 79.90, "Cabos"),

    ("Cabo USB-C", 49.90, "Cabos"),

    ("Carregador USB-C", 99.90, "Energia"),

    ("Filtro de Linha", 89.90, "Energia")

]


for produto in produtos:

    cursor.execute(
        """
        SELECT id
        FROM produtos
        WHERE nome = ?
        """,
        (produto[0],)
    )

    produto_existente = cursor.fetchone()


    if not produto_existente:

        cursor.execute(
            """
            INSERT INTO produtos
            (nome, preco, categoria)
            VALUES (?, ?, ?)
            """,
            produto
        )


conexao.commit()

conexao.close()


print("Produtos adicionados com sucesso!")