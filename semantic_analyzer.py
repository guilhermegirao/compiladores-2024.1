import re
from tokens import TOKENS

class Node:
	def __init__(self, name, var_type=None, value=None):
		self.name = name
		self.var_type = var_type
		self.value = value

class LookupTable:
	def __init__(self):
		self.table = {}

	def add_variable(self, var_name, node):
		if var_name in self.table:
			return False

		self.table[var_name] = node
		return True

	def get_variable(self, var_name):
		return self.table.get(var_name)

class SemanticAnalyzer:
	def __init__(self):
		self.lookup_table = LookupTable()
		self.errors = []

	def is_value_compatible(self, var_type, value):
		if re.match(TOKENS["INT"], var_type):
			return re.match(TOKENS["NUM"], value) is not None

		if re.match(TOKENS["STRING"], var_type):
			return re.match(TOKENS["CONST"], value) is not None

		return False

	def evaluate_expression(self, expression):
		tokens = re.findall(
			rf'{TOKENS["VAR"]}|{TOKENS["NUM"]}|{TOKENS["CONST"]}|{TOKENS["ADD"]}|{TOKENS["SUB"]}|{TOKENS["MUL"]}|{TOKENS["DIV"]}|{TOKENS["MOD"]}|{TOKENS["GT"]}|{TOKENS["LT"]}|{TOKENS["LPAREN"]}|{TOKENS["RPAREN"]}',
			expression
		)

		if not self.check_parentheses(tokens):
			self.errors.append("Parênteses não balanceados.")
			return None

		postfix = self.infix_to_postfix(tokens)

		if postfix is None:
			self.errors.append("Expressão inválida.")
			return None

		result_type = self.evaluate_postfix(postfix)
		return result_type

	def check_parentheses(self, tokens):
		stack = []
		for token in tokens:
			if token == '(':
				stack.append('(')
			elif token == ')':
				if not stack or stack.pop() != '(':
					return False
		return len(stack) == 0

	def infix_to_postfix(self, tokens):
		precedence = {'>': 0, '<': 0, '+': 1, '-': 1, '*': 2, '/': 2, '%': 2}
		output = []
		operators = []

		for token in tokens:
			if re.match(TOKENS["NUM"], token) or re.match(TOKENS["CONST"], token):
				output.append(token)
			elif token in precedence:
				while (operators and operators[-1] in precedence and 
							 precedence[token] <= precedence[operators[-1]]):
					output.append(operators.pop())
				operators.append(token)

		while operators:
			op = operators.pop()
			output.append(op)

		return output

	def evaluate_postfix(self, tokens):
		stack = []
		for token in tokens:
			if re.match(TOKENS["NUM"], token):
				stack.append("int")
			elif re.match(TOKENS["CONST"], token):
				stack.append("string")
			elif re.match(TOKENS["VAR"], token):
				var_node = self.lookup_table.get_variable(token)
				if var_node:
					stack.append(var_node.var_type)
				else:
					self.errors.append(f"Variável '{token}' não declarada.")
					return None
			elif token in {'+', '-', '*', '/', '%', '>', '<'}:
				if len(stack) < 2:
					self.errors.append(f"Expressão inválida.")
					return None
				type2 = stack.pop()
				type1 = stack.pop()
				if token in {'+', '-', '*', '/', '%'}:
					if type1 != type2:
						self.errors.append(f"Operação entre tipos incompatíveis '{type1}' e '{type2}'.")
						return None
					stack.append(type1)
				elif token in {'>', '<'}:
					if type1 != 'int' or type2 != 'int':
						self.errors.append(f"Operador '{token}' deve ser usado com inteiros.")
						return None
					stack.append('int')
			else:
				self.errors.append(f"Token inválido '{token}'.")
				return None
		return stack[0] if stack else None

	def add_operation(self, result_var, expression, expected_type):
		result_type = self.evaluate_expression(expression)
		if result_type is None:
			return

		if result_type != expected_type:
			self.errors.append(f"Atribuição inválida: esperado {expected_type}, encontrado {result_type}.")
			return

		# Atualiza o nó existente na LookupTable
		result_node = self.lookup_table.get_variable(result_var)
		if result_node:
			result_node.var_type = result_type
			result_node.value = expression
		else:
			result_node = Node(result_var, result_type, expression)
			self.lookup_table.add_variable(result_var, result_node)

	def parse_and_analyze(self, source_code):
		lines = source_code.split(';')
		for line in lines:
			line = line.strip()
			if not line:
				continue

			if match := re.match(
					rf'({TOKENS["INT"]}|{TOKENS["STRING"]})\s+({TOKENS["VAR"]})\s*{TOKENS["EQ"]}\s*(.+)', 
					line
			):
				var_type, var_name, expression = match.groups()
				expression = expression.strip()

				# Verifica se a variável foi declarada
				if self.lookup_table.get_variable(var_name):
					self.errors.append(f"Erro: Variável '{var_name}' já declarada.")
					continue

				# Verifica se a expressão é compatível com o tipo
				result_type = self.evaluate_expression(expression)
				if result_type is None:
					continue

				if result_type != var_type:
					self.errors.append(f"Atribuição inválida para '{var_name}': esperado {var_type}, encontrado {result_type}.")
					continue

				var_node = Node(var_name, var_type, expression)
				self.lookup_table.add_variable(var_name, var_node)
			elif match := re.match(
					rf'({TOKENS["VAR"]})\s*{TOKENS["EQ"]}\s*(.+)', 
					line
			):
				var_name, expression = match.groups()
				expression = expression.strip()

				# Verifica se a variável foi declarada
				if not self.lookup_table.get_variable(var_name):
					self.errors.append(f"Variável '{var_name}' não declarada.")
					continue

				var_type = self.lookup_table.get_variable(var_name).var_type
				# Adiciona operação se a expressão estiver correta
				self.add_operation(var_name, expression, var_type)
			else:
				self.errors.append(f"Declaração inválida: {line}")

	def analyze(self):
		return len(self.errors) == 0, self.errors

# Exemplo de uso
source_code = """
int Z = (1 + 1 + 1);
int Z = (1 + 1 + 1);
"""

analyzer = SemanticAnalyzer()
analyzer.parse_and_analyze(source_code)
success, errors = analyzer.analyze()

print("Sucesso" if success else "Falha")
for error in errors:
	print(error)
