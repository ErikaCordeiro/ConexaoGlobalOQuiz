from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave-secreta'

# Criação do banco
def criar_banco():
    if os.path.exists("quiz.db"):
        return

    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT NOT NULL,
            alternativa_a TEXT NOT NULL,
            alternativa_b TEXT NOT NULL,
            alternativa_c TEXT NOT NULL,
            alternativa_d TEXT NOT NULL,
            resposta_correta TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            pontuacao INTEGER NOT NULL,
            data TEXT NOT NULL
        )
    """)

    perguntas = [
        ("Qual a capital do Brasil?", "São Paulo", "Brasília", "Rio de Janeiro", "Belo Horizonte", "b"),
        ("Qual é o maior planeta do Sistema Solar?", "Terra", "Vênus", "Júpiter", "Saturno", "c"),
        ("Quem escreveu 'Dom Casmurro'?", "Machado de Assis", "José de Alencar", "Carlos Drummond", "Clarice Lispector", "a"),
        ("Qual é o símbolo químico da água?", "O2", "H2O", "CO2", "NaCl", "b"),
        ("Quanto é 7 x 8?", "54", "56", "64", "58", "b"),
        ("Qual o idioma falado na Austrália?", "Inglês", "Alemão", "Francês", "Espanhol", "a"),
        ("Quem pintou a Mona Lisa?", "Van Gogh", "Leonardo da Vinci", "Pablo Picasso", "Michelangelo", "b"),
        ("Qual é o oceano entre África e América?", "Atlântico", "Pacífico", "Índico", "Ártico", "a"),
        ("Quantos continentes existem?", "5", "6", "7", "8", "c"),
        ("Quem descobriu o Brasil?", "Pedro Álvares Cabral", "Cristóvão Colombo", "Dom Pedro I", "Vasco da Gama", "a")
    ]

    cursor.executemany("""
        INSERT INTO perguntas (pergunta, alternativa_a, alternativa_b, alternativa_c, alternativa_d, resposta_correta)
        VALUES (?, ?, ?, ?, ?, ?)
    """, perguntas)

    conn.commit()
    conn.close()

criar_banco()

def get_perguntas():
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, pergunta, alternativa_a, alternativa_b, alternativa_c, alternativa_d, resposta_correta FROM perguntas")
    perguntas = cursor.fetchall()
    conn.close()
    return perguntas

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def iniciar_quiz():
    nome = request.form.get("nome")
    session["nome"] = nome
    session["pontuacao"] = 0
    session["respostas_usuario"] = []
    return redirect(url_for("quiz", num=1))

@app.route("/quiz/<int:num>")
def quiz(num):
    perguntas = get_perguntas()
    if num > len(perguntas):
        return redirect(url_for("resultado"))

    pergunta = perguntas[num - 1]
    nome = session.get("nome", "Anônimo")
    return render_template("quiz.html", num=num, pergunta=pergunta, total=len(perguntas), nome=nome)

@app.route("/responder", methods=["POST"])
def responder():
    resposta = request.form.get("resposta")
    num_str = request.form.get("num")

    if num_str is None or not num_str.isdigit():
        return "Número da pergunta inválido", 400

    num = int(num_str)
    perguntas = get_perguntas()

    if num < 1 or num > len(perguntas):
        return "Pergunta inválida", 400

    correta = perguntas[num - 1][6]

    session["respostas_usuario"].append({
        "pergunta": perguntas[num - 1][1],
        "alternativas": perguntas[num - 1][2:6],
        "resposta_correta": correta,
        "resposta_usuario": resposta
    })

    if resposta == correta:
        session["pontuacao"] += 1

    proxima = num + 1
    if proxima > len(perguntas):
        return redirect(url_for("resultado"))
    else:
        return redirect(url_for("quiz", num=proxima))

@app.route("/resultado")
def resultado():
    nome = session.get("nome", "Anônimo")
    pontuacao = session.get("pontuacao", 0)
    respostas_usuario = session.get("respostas_usuario", [])
    data = datetime.now().strftime("%d/%m/%Y %H:%M")

    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ranking (nome, pontuacao, data) VALUES (?, ?, ?)", (nome, pontuacao, data))
    conn.commit()

    cursor.execute("SELECT nome, pontuacao, data FROM ranking ORDER BY pontuacao DESC, data ASC LIMIT 10")
    ranking = cursor.fetchall()
    conn.close()

    respostas_formatadas = []
    letras = ['a', 'b', 'c', 'd']

    for r in respostas_usuario:
        idx_correta = letras.index(r["resposta_correta"])
        resposta_correta_texto = r["alternativas"][idx_correta]
        resposta_usuario_texto = r["alternativas"][letras.index(r["resposta_usuario"])]
        correta = r["resposta_usuario"] == r["resposta_correta"]

        respostas_formatadas.append({
            "pergunta": r["pergunta"],
            "resposta": resposta_usuario_texto,
            "resposta_correta": resposta_correta_texto,
            "correta": correta
        })

    total_perguntas = len(get_perguntas())

    return render_template("resultado.html",
                           nome=nome,
                           pontuacao=pontuacao,
                           total_perguntas=total_perguntas,
                           ranking=ranking,
                           respostas=respostas_formatadas)

@app.route("/zerar-ranking")
def zerar_ranking():
    senha = request.args.get("senha")
    if senha != "minha_senha_supersecreta":
        return "❌ Acesso negado."

    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ranking")
    conn.commit()
    conn.close()
    return "✅ Ranking zerado com sucesso!"

if __name__ == "__main__":
    app.run(debug=True)
