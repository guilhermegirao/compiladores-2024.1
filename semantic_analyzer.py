import re

from utils.tokens import TOKENS, LITERALS
from lookup_table.node import Node
from lookup_table.lookup_table import LookupTable

class SemanticAnalyzer:
	def __init__(self):
		self.lookup_table = LookupTable()
		self.errors = []

	def match_token(self, pattern, token):
		return re.match(TOKENS[pattern], token) is not None

	def tokenize_expression(self, expression):
		pattern = (
			rf'{TOKENS["VAR"]}|{TOKENS["NUM"]}|{TOKENS["CONST"]}|{TOKENS["ADD"]}|'
			rf'{TOKENS["SUB"]}|{TOKENS["MUL"]}|{TOKENS["GT"]}|{TOKENS["LT"]}'
			rf'{TOKENS["LPAREN"]}|{TOKENS["RPAREN"]}'
		)

		return re.findall(pattern, expression)

	def check_parentheses(self, tokens):
		stack = []

		for token in tokens:
			if token == '(':
				stack.append('(')

			if token == ')' and (not stack or stack.pop() != '('):
				return False

		return len(stack) == 0

	def evaluate_expression(self, expression):
		tokens = self.tokenize_expression(expression)

		if not self.check_parentheses(tokens):
			self.errors.append("Parênteses não balanceados.")
			return None

		postfix = self.expression_to_postfix(tokens)

		if postfix is None:
			self.errors.append("Expressão inválida.")
			return None

		result_type = self.evaluate_postfix(postfix)
		return result_type

	def expression_to_postfix(self, tokens):
		precedence = {'>': 0, '<': 0, '+': 1, '-': 1, '*': 2}
		output = []
		operators = []

		for token in tokens:
			if self.match_token("NUM", token) or self.match_token("CONST", token) or self.match_token("VAR", token):
				output.append(token)
			elif token in precedence:
				while (operators and operators[-1] in precedence and
								precedence[token] <= precedence[operators[-1]]):
					output.append(operators.pop())
				operators.append(token)
			elif token == '(':
				operators.append(token)
			elif token == ')':
				while operators and operators[-1] != '(':
					output.append(operators.pop())
				operators.pop()

		while operators:
			output.append(operators.pop())

		print(output)

		return output

	def evaluate_postfix(self, tokens):
		stack = []
		for token in tokens:
			if self.match_token("NUM", token):
				stack.append("int")
				continue

			if self.match_token("CONST", token):
				stack.append("string")
				continue

			if self.match_token("VAR", token):
				var_node = self.lookup_table.get_variable(token)
				if var_node:
					stack.append(var_node.var_type)
				else:
					self.errors.append(f"Variável '{token}' não declarada.")
					return None
				continue

			if token in {'+', '-', '*', '>', '<'}:
				if len(stack) < 2:
					self.errors.append(f"Expressão inválida.")
					return None

				type2 = stack.pop()
				type1 = stack.pop()

				if type1 != type2:
					self.errors.append(f"Operação entre tipos incompatíveis '{type1}' e '{type2}'.")
					return None

				if type1 != 'int' or type2 != 'int':
					self.errors.append(f"Operador '{token}' deve ser usado com inteiros.")
					return None
				stack.append('int')
				continue

			self.errors.append(f"Token inválido '{token}'.")
			return None

		return stack[0] if stack else None

	def parse_and_analyze(self, source_code):
		lines = source_code.split(';')

		# Avalia todas as linhas separadas por ; do bloco
		for line in lines:
			line = line.strip()
			if not line:
				continue

			# Verifica se a linha é uma declaração de variável
			if match := re.match(
				rf'({TOKENS["INT"]}|{TOKENS["STRING"]})\s+({TOKENS["VAR"]})\s*{TOKENS["EQ"]}\s*(.+)', 
				line
			):
				var_type, var_name, expression = match.groups()
				expression = expression.strip()

				# Verifica se a variável foi declarada
				if self.lookup_table.get_variable(var_name):
					self.errors.append(f"Erro: Variável '{var_name}' já declarada.")
					return

				# Verifica se a expressão é compatível com o tipo
				result_type = self.evaluate_expression(expression)
				if result_type is None:
					return

				if result_type != var_type:
					self.errors.append(f"Atribuição inválida para '{var_name}': esperado {var_type}, encontrado {result_type}.")
					return

				var_node = Node(var_name, var_type, expression)
				self.lookup_table.add_variable(var_name, var_node)
				continue

			# Verifica se a linha é uma atribuição de variável
			if match := re.match(
				rf'({TOKENS["VAR"]})\s*{TOKENS["EQ"]}\s*(.+)', 
				line
			):
				var_name, expression = match.groups()
				expression = expression.strip()

				var_node = self.lookup_table.get_variable(var_name)

				# Verifica se a variável foi declarada
				if not var_node:
					self.errors.append(f"Variável '{var_name}' não declarada.")
					return

				var_type = self.lookup_table.get_variable(var_name).var_type

				result_type = self.evaluate_expression(expression)
				if result_type is None:
					return

				if result_type != var_type:
					self.errors.append(f"Atribuição inválida: esperado {var_type}, encontrado {result_type}.")
					return

				# Atualiza o nó existente na LookupTable
				var_node.update(var_type, expression)

				continue

			self.errors.append(f"Declaração inválida: {line}")

	def response(self):
		return len(self.errors) == 0, self.errors
