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

# Função para adicionar a coluna 'pontos' caso não exista
def adicionar_coluna_pontos():
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE ranking ADD COLUMN pontos INTEGER")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # A coluna já existe
    conn.close()

# Perguntas fixas (10 perguntas completas)
perguntas = [
    ("Qual a capital do Brasil?", "a) São Paulo", "b) Brasília", "c) Rio de Janeiro", "d) Belo Horizonte"),
    ("Quem foi o primeiro presidente do Brasil?", "a) Marechal Deodoro da Fonseca", "b) Getúlio Vargas", "c) Dom Pedro I", "d) Juscelino Kubitschek"),
    ("Qual é o maior planeta do sistema solar?", "a) Terra", "b) Marte", "c) Júpiter", "d) Saturno"),
    ("Quem pintou a Mona Lisa?", "a) Van Gogh", "b) Leonardo da Vinci", "c) Pablo Picasso", "d) Michelangelo"),
    ("Qual é a fórmula da água?", "a) CO2", "b) H2O", "c) O2", "d) NaCl"),
    ("Em que país está localizada a Torre Eiffel?", "a) Itália", "b) Alemanha", "c) França", "d) Espanha"),
    ("Qual é o maior oceano do mundo?", "a) Atlântico", "b) Índico", "c) Ártico", "d) Pacífico"),
    ("Em que continente fica o Egito?", "a) Ásia", "b) África", "c) Europa", "d) América"),
    ("Qual é a moeda oficial dos Estados Unidos?", "a) Euro", "b) Peso", "c) Dólar", "d) Libra"),
    ("Quem escreveu 'Dom Casmurro'?", "a) Machado de Assis", "b) José de Alencar", "c) Lima Barreto", "d) Clarice Lispector"),
]

# Respostas corretas (usando o índice da alternativa)
respostas_corretas = ['b', 'a', 'c', 'b', 'b', 'c', 'd', 'b', 'c', 'a']

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
    num = int(request.form["num"]) - 1  # Ajuste para o índice correto
    resposta = request.form["resposta"]
    nome = request.form["nome"]
    pontos = int(request.args.get("pontos", 0))

    correta = respostas_corretas[num]  # Obtemos a resposta correta

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

    return render_template("resultado.html", pontuacao=pontos,
                           total_perguntas=len(perguntas),
                           ranking=ranking)

# Inicializa o banco ao importar o app
criar_tabela()
adicionar_coluna_pontos()

# Roda o app localmente
if __name__ == "__main__":
    app.run(debug=True)
