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
        pontos INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Perguntas fixas
perguntas = [
    ("Qual a capital do Brasil?", "São Paulo", "Brasília", "Rio de Janeiro", "Belo Horizonte", "b"),
    ("Qual é o maior planeta do sistema solar?", "Terra", "Marte", "Júpiter", "Saturno", "c"),
    ("Quem pintou a Mona Lisa?", "Van Gogh", "Da Vinci", "Picasso", "Michelangelo", "b"),
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
    nome = request.args.get("nome")
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
    pontos = int(request.args.get("pontos"))

    # Salvar no ranking
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ranking (nome, pontos) VALUES (?, ?)", (nome, pontos))
    conn.commit()

    # Top 10
    cursor.execute("SELECT nome, pontos FROM ranking ORDER BY pontos DESC, id ASC LIMIT 10")
    ranking = cursor.fetchall()
    conn.close()

    # Lista com todas as respostas e corretas (estático por enquanto)
    respostas = []
    for i, p in enumerate(perguntas):
        respostas.append({
            "pergunta": p[0],
            "resposta": "Resposta do usuário",  # você pode implementar para salvar isso depois
            "correta": False,
            "resposta_correta": p[{"a": 1, "b": 2, "c": 3, "d": 4}[p[5]]]
        })

    return render_template("resultado.html", pontuacao=pontos, total_perguntas=len(perguntas),
                           respostas=respostas, ranking=ranking)

# Inicializa o banco ao importar o app
criar_tabela()

# Roda o app localmente
if __name__ == "__main__":
    app.run()
