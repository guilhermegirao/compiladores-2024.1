from semantic_analyzer import SemanticAnalyzer

def evaluateResponse(success):
  return "Sucesso" if success else "Falha"

"""
TODO:
- criar casos de uso
- criar doc de como rodar
- organizar o código
- criar erros genericos tipo i18n (opcional)
- substituir valores fixos pelos literals (opcional)
"""

if __name__ == "__main__":
  source_code = """
  int a = 1 + 2;
  string a = 1;
  """

  analyzer = SemanticAnalyzer()
  analyzer.analyze(source_code)
  success, errors = analyzer.response()

  print(evaluateResponse(success))
  print(f"Erro: {"\n".join(errors)}")