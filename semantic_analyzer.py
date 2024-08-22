import re

from utils.tokens import TOKENS
from lookup_table.node import Node
from lookup_table.lookup_table import LookupTable

class SemanticAnalyzer:
  def __init__(self):
    self.lookup_table = LookupTable()
    self.errors = []

  def get_alphabet(self):
    # Retorna uma expressão regular combinada de todos os tokens relevantes que compõem o alfabeto.
    return (
      rf'{TOKENS["VAR"]}|{TOKENS["NUM"]}|{TOKENS["CONST"]}|{TOKENS["ADD"]}|'
      rf'{TOKENS["SUB"]}|{TOKENS["MUL"]}|{TOKENS["GT"]}|{TOKENS["LT"]}|'
      rf'{TOKENS["LPAREN"]}|{TOKENS["RPAREN"]}'
    )

  def match_token(self, pattern, token):
    # Verifica se o token corresponde ao padrão especificado.
    return re.match(TOKENS[pattern], token) is not None

  def tokenize_expression(self, expression):
    # Converte a expressão em tokens válidos e identifica tokens inválidos.
    pattern = self.get_alphabet()
    valid_tokens = re.findall(pattern, expression)

    # Combina todos os tokens válidos e inválidos.
    combined_pattern = rf'{pattern}|[^\s]'
    all_tokens = re.findall(combined_pattern, expression)

    # Identifica tokens inválidos que não correspondem ao padrão.
    invalid_tokens = [token for token in all_tokens if token not in valid_tokens]

    return valid_tokens, invalid_tokens

  def check_parentheses(self, tokens):
    # Verifica se os parênteses na lista de tokens estão balanceados.
    stack = []

    for token in tokens:
      if token == '(':
        stack.append('(')

      if token == ')' and (not stack or stack.pop() != '('):
        return False

    return len(stack) == 0

  def evaluate_expression(self, expression):
    # Avalia a expressão fornecida, convertendo-a em postfixed e verificando a validade.
    tokens, invalid_tokens = self.tokenize_expression(expression)

    # Verifica se há tokens inválidos.
    if invalid_tokens:
      self.errors.append(f"Token inválido: {invalid_tokens[0]}")
      return None

    # Verifica se os parênteses estão balanceados.
    if not self.check_parentheses(tokens):
      self.errors.append("Parênteses não balanceados.")
      return None

    # Converte a expressão para a forma postfixed.
    postfix = self.expression_to_postfix(tokens)

    if postfix is None:
      self.errors.append("Expressão inválida.")
      return None

    result_type = self.evaluate_postfix(postfix)
    return result_type

  def expression_to_postfix(self, tokens):
    # Converte a expressão em postfixed utilizando a precedência dos operadores e dos parêntesis.
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

    return output

  def evaluate_postfix(self, tokens):
    # Avalia a expressão postfixed e verifica a compatibilidade de tipos.
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

  def analyze(self, code):
    # Analisa e avalia cada linha do bloco separada por ponto e vírgula.
    lines = code.split(';')

    for line in lines:
      line = line.strip()
      if not line:
        continue

      # Verifica se a linha é uma declaração de variável.
      if match := re.match(
        rf'({TOKENS["INT"]}|{TOKENS["STRING"]})\s+({TOKENS["VAR"]})\s*{TOKENS["EQ"]}\s*(.+)',
        line
      ):
        var_type, var_name, expression = match.groups()
        expression = expression.strip()

        # Verifica se a variável já foi declarada.
        if self.lookup_table.get_variable(var_name):
          self.errors.append(f"Variável '{var_name}' já declarada.")
          return

        # Verifica se a expressão é compatível com o tipo da variável.
        result_type = self.evaluate_expression(expression)
        if result_type is None:
          return

        if result_type != var_type:
          self.errors.append(f"Atribuição inválida para '{var_name}': esperado {var_type}, encontrado {result_type}.")
          return

        var_node = Node(var_name, var_type, expression)
        self.lookup_table.add_variable(var_name, var_node)
        continue

      # Verifica se a linha é uma atribuição a uma variável existente.
      if match := re.match(
        rf'({TOKENS["VAR"]})\s*{TOKENS["EQ"]}\s*(.+)', 
        line
      ):
        var_name, expression = match.groups()
        expression = expression.strip()

        var_node = self.lookup_table.get_variable(var_name)

        # Verifica se a variável foi declarada anteriormente.
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

        # Atualiza o nó existente na LookupTable com a nova expressão.
        var_node.update(var_type, expression)
        continue

      self.errors.append(f"Declaração inválida: {line}")

  def response(self):
    return len(self.errors) == 0, self.errors
