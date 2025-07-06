from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Banco de dados
def criar_tabela():
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ranking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        pontuacao INTEGER NOT NULL DEFAULT 0,
        data TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
    )
    """)
    conn.commit()
    conn.close()

# Perguntas fixas (10 perguntas completas)
perguntas = [
    ("Qual a capital do Brasil?", "a) São Paulo", "b) Brasília", "c) Rio de Janeiro", "d) Belo Horizonte", "b"),
    ("Quem foi o primeiro presidente do Brasil?", "a) Marechal Deodoro da Fonseca", "b) Getúlio Vargas", "c) Dom Pedro I", "d) Juscelino Kubitschek", "a"),
    ("Qual é o maior planeta do sistema solar?", "a) Terra", "b) Marte", "c) Júpiter", "d) Saturno", "c"),
    ("Quem pintou a Mona Lisa?", "a) Van Gogh", "b) Leonardo da Vinci", "c) Pablo Picasso", "d) Michelangelo", "b"),
    ("Qual é a fórmula da água?", "a) CO2", "b) H2O", "c) O2", "d) NaCl", "b"),
    ("Em que país está localizada a Torre Eiffel?", "a) Itália", "b) Alemanha", "c) França", "d) Espanha", "c"),
    ("Qual é o maior oceano do mundo?", "a) Atlântico", "b) Índico", "c) Ártico", "d) Pacífico", "d"),
    ("Em que continente fica o Egito?", "a) Ásia", "b) África", "c) Europa", "d) América", "b"),
    ("Qual é a moeda oficial dos Estados Unidos?", "a) Euro", "b) Peso", "c) Dólar", "d) Libra", "c"),
    ("Quem escreveu 'Dom Casmurro'?", "a) Machado de Assis", "b) José de Alencar", "c) Lima Barreto", "d) Clarice Lispector", "a"),
]

# Rota inicial
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Iniciar quiz
@app.route("/iniciar", methods=["POST"])
def iniciar_quiz():
    nome = request.form["nome"]
    return redirect(url_for("quiz", nome=nome, num=0, pontos=0))

# Rota das perguntas
@app.route("/quiz")
def quiz():
    nome = request.args.get("nome")
    num = int(request.args.get("num"))
    pontos = int(request.args.get("pontos"))

    if num < len(perguntas):
        return render_template("quiz.html",
                               nome=nome,
                               num=num + 1,
                               total=len(perguntas),
                               pergunta=perguntas[num])
    else:
        return redirect(url_for("resultado", nome=nome, pontos=pontos))

# Processar resposta
@app.route("/responder", methods=["POST"])
def responder():
    num = int(request.form["num"]) - 1
    resposta = request.form["resposta"]
    nome = request.form["nome"]  # Corrigido: vem do formulário
    pontos = int(request.args.get("pontos", 0))

    pergunta = perguntas[num]
    correta = pergunta[5]

    if resposta == correta:
        pontos += 1

    return redirect(url_for("quiz", nome=nome, num=num + 1, pontos=pontos))

# Resultado final
@app.route("/resultado")
def resultado():
    nome = request.args.get("nome")
    pontos = int(request.args.get("pontos", 0))  # Garantir que o valor de pontos seja válido

    # Verificar se a variável pontos está corretamente definida
    if pontos is None:
        pontos = 0  # Se for None, atribuímos 0 (valor padrão)

    # Salvar no ranking
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ranking (nome, pontuacao, data) 
        VALUES (?, ?, datetime('now', 'localtime'))
    """, (nome, pontos))  # Inserir a data atual diretamente
    conn.commit()

    # Top 10
    cursor.execute("SELECT nome, pontuacao FROM ranking ORDER BY pontuacao DESC, id ASC LIMIT 10")  # Corrigido o nome da coluna
    ranking = cursor.fetchall()
    conn.close()

    return render_template("resultado.html", pontuacao=pontos,
                           total_perguntas=len(perguntas),
                           ranking=ranking)

# Inicializa o banco ao importar o app
criar_tabela()

# Roda o app localmente
if __name__ == "__main__":
    app.run(debug=True)
