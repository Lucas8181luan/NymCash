from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'nymcash_secret_key'
# Dados simulados em memória
usuarios = {"admin": "1234"}

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session.get('usuario'):
			flash('Faça login para acessar esta página.', 'warning')
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		usuario = request.form['usuario']
		senha = request.form['senha']
		if usuario in usuarios and usuarios[usuario] == senha:
			session['usuario'] = usuario
			flash('Login realizado com sucesso!', 'success')
			return redirect(url_for('index'))
		else:
			flash('Usuário ou senha inválidos.', 'danger')
	return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('usuario', None)
	flash('Logout realizado com sucesso!', 'success')
	return redirect(url_for('login'))

# Dados simulados em memória
transacoes = [
	{"tipo": "entrada", "valor": 2000.00, "descricao": "Salário", "data": "01/12/2025"},
	{"tipo": "saida", "valor": 150.00, "descricao": "Mercado", "data": "02/12/2025"}
]
contas = [
	{"nome": "Conta Corrente", "saldo": 2000.00},
	{"nome": "Poupança", "saldo": 1500.00}
]
cartoes = [
	{"nome": "Visa", "limite": 3000.00},
	{"nome": "Mastercard", "limite": 2500.00}
]
metas = [
	{"meta": "Viagem", "valor": 5000.00},
	{"meta": "Reserva de emergência", "valor": 10000.00}
]
clubes = [
	{"nome": "Clube dos Investidores", "descricao": "Investimentos e finanças"},
	{"nome": "Clube de Economia", "descricao": "Dicas de economia"}
]

@app.route('/')
@login_required
def index():
	saldo_atual = sum([c["saldo"] for c in contas])
	ganhos_mes = sum([t["valor"] for t in transacoes if t["tipo"] == "entrada"])
	gastos_mes = sum([t["valor"] for t in transacoes if t["tipo"] == "saida"])
	resultado = ganhos_mes - gastos_mes
	return render_template('index.html', saldo_atual=saldo_atual, ganhos_mes=ganhos_mes, gastos_mes=gastos_mes, resultado=resultado)

@app.route('/registrar-transacao', methods=['GET', 'POST'])
@login_required
def registrar_transacao():
	if request.method == 'POST':
		tipo = request.form['tipo']
		try:
			valor = float(request.form['valor'])
		except ValueError:
			flash('Valor inválido.', 'danger')
			return redirect(url_for('registrar_transacao'))
		descricao = request.form['descricao']
		from datetime import datetime
		data = datetime.now().strftime('%d/%m/%Y')
		transacoes.insert(0, {"tipo": tipo, "valor": valor, "descricao": descricao, "data": data})
		flash('Transação registrada com sucesso!', 'success')
		return redirect(url_for('registrar_transacao'))
	return render_template('registrar_transacao.html', transacoes=transacoes[:5])

@app.route('/extrato', methods=['GET', 'POST'])
@login_required
def extrato():
	filtradas = transacoes
	tipo = request.args.get('tipo', '')
	descricao = request.args.get('descricao', '').lower()
	data = request.args.get('data', '')
	if tipo:
		filtradas = [t for t in filtradas if t['tipo'] == tipo]
	if descricao:
		filtradas = [t for t in filtradas if descricao in t['descricao'].lower()]
	if data:
		filtradas = [t for t in filtradas if t['data'] == data]
	ganhos_mes = sum([t["valor"] for t in filtradas if t["tipo"] == "entrada"])
	gastos_mes = sum([t["valor"] for t in filtradas if t["tipo"] == "saida"])
	resultado = ganhos_mes - gastos_mes
	return render_template('extrato.html', transacoes=filtradas, ganhos_mes=ganhos_mes, gastos_mes=gastos_mes, resultado=resultado, tipo=tipo, descricao=descricao, data=data)

@app.route('/minhas-contas', methods=['GET', 'POST'])
@login_required
def minhas_contas():
	filtradas = contas
	nome = request.args.get('nome', '').lower()
	saldo_min = request.args.get('saldo_min', '')
	saldo_max = request.args.get('saldo_max', '')
	if nome:
		filtradas = [c for c in filtradas if nome in c['nome'].lower()]
	if saldo_min:
		try:
			filtradas = [c for c in filtradas if c['saldo'] >= float(saldo_min)]
		except ValueError:
			pass
	if saldo_max:
		try:
			filtradas = [c for c in filtradas if c['saldo'] <= float(saldo_max)]
		except ValueError:
			pass
	if request.method == 'POST':
		nome_c = request.form['nome_conta']
		try:
			saldo = float(request.form['saldo_inicial'])
		except ValueError:
			flash('Saldo inválido.', 'danger')
			return redirect(url_for('minhas_contas'))
		contas.append({"nome": nome_c, "saldo": saldo})
		flash('Conta adicionada com sucesso!', 'success')
		return redirect(url_for('minhas_contas'))
	return render_template('minhas_contas.html', contas=filtradas, nome=nome, saldo_min=saldo_min, saldo_max=saldo_max)

@app.route('/cartao-de-credito', methods=['GET', 'POST'])
@login_required
def cartao_de_credito():
	filtradas = cartoes
	nome = request.args.get('nome', '').lower()
	limite_min = request.args.get('limite_min', '')
	limite_max = request.args.get('limite_max', '')
	if nome:
		filtradas = [c for c in filtradas if nome in c['nome'].lower()]
	if limite_min:
		try:
			filtradas = [c for c in filtradas if c['limite'] >= float(limite_min)]
		except ValueError:
			pass
	if limite_max:
		try:
			filtradas = [c for c in filtradas if c['limite'] <= float(limite_max)]
		except ValueError:
			pass
	if request.method == 'POST':
		nome_c = request.form['nome_cartao']
		try:
			limite = float(request.form['limite'])
		except ValueError:
			flash('Limite inválido.', 'danger')
			return redirect(url_for('cartao_de_credito'))
		cartoes.append({"nome": nome_c, "limite": limite})
		flash('Cartão adicionado com sucesso!', 'success')
		return redirect(url_for('cartao_de_credito'))
	return render_template('cartao_de_credito.html', cartoes=filtradas, nome=nome, limite_min=limite_min, limite_max=limite_max)

@app.route('/meu-planejador', methods=['GET', 'POST'])
@login_required
def meu_planejador():
	filtradas = metas
	meta = request.args.get('meta', '').lower()
	valor_min = request.args.get('valor_min', '')
	valor_max = request.args.get('valor_max', '')
	if meta:
		filtradas = [m for m in filtradas if meta in m['meta'].lower()]
	if valor_min:
		try:
			filtradas = [m for m in filtradas if m['valor'] >= float(valor_min)]
		except ValueError:
			pass
	if valor_max:
		try:
			filtradas = [m for m in filtradas if m['valor'] <= float(valor_max)]
		except ValueError:
			pass
	if request.method == 'POST':
		meta_c = request.form['meta']
		try:
			valor = float(request.form['valor_meta'])
		except ValueError:
			flash('Valor inválido.', 'danger')
			return redirect(url_for('meu_planejador'))
		metas.append({"meta": meta_c, "valor": valor})
		flash('Meta adicionada com sucesso!', 'success')
		return redirect(url_for('meu_planejador'))
	return render_template('meu_planejador.html', metas=filtradas, meta=meta, valor_min=valor_min, valor_max=valor_max)

@app.route('/meu-clube', methods=['GET', 'POST'])
@login_required
def meu_clube():
	filtradas = clubes
	nome = request.args.get('nome', '').lower()
	descricao = request.args.get('descricao', '').lower()
	if nome:
		filtradas = [c for c in filtradas if nome in c['nome'].lower()]
	if descricao:
		filtradas = [c for c in filtradas if descricao in c['descricao'].lower()]
	if request.method == 'POST':
		nome_c = request.form['nome_clube']
		descricao_c = request.form['descricao_clube']
		clubes.append({"nome": nome_c, "descricao": descricao_c})
		flash('Clube criado com sucesso!', 'success')
		return redirect(url_for('meu_clube'))
	return render_template('meu_clube.html', clubes=filtradas, nome=nome, descricao=descricao)

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port)
