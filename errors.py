ERROR_CODES = {
  "NO_BALANCED_PAREN": "Parênteses não balanceados.",
  "INVALID_EXPRESSION": "Expressão inválida.",
  "UNDECLARED_VARIABLE": "Variável %var% não declarada.",
  "TYPE_MISMATCH": "Operação entre tipos incompatíveis %expected% e %received%.",
  "INVALID_OPERATOR": "Operador %op% deve ser usado com inteiros.",
  "INVALID_TOKEN": "Token inválido %token%.",
  "ALREADY_DECLARED": "Variável %var% já declarada.",
  "INVALID_ASSIGNMENT": "Atribuição inválida para %var: esperado %expected%, encontrado %found%.",
  "INVALID_DECLARATION": "Declaração inválida: %expr%"
}

class Errors:
  def __init__(self):
    self.errors = []

  def add_error(self, error_code, **kwargs):
    error_message = ERROR_CODES[error_code]
    for key, value in kwargs.items():
      error_message = error_message.replace(f"%{key}%", value)
    self.errors.append(error_message)

  def get_errors(self):
    return self.errors

  def has_errors(self):
    return bool(self.errors)