from semantic_analyzer import SemanticAnalyzer

def evaluateResponse(success, errors):
  print("Sucesso" if success else "Falha")
  if errors:
    print(f"Erro: {"\n".join(errors)}")

"""
TODO:
- corrigir caso de inicialização sem =, ex.: int a;
"""

if __name__ == "__main__":
  code_block = ""

  with open("__tests__/input.txt", "r") as file:
    code_block = file.read()

  analyzer = SemanticAnalyzer()
  analyzer.analyze(code_block)

  success, errors = analyzer.response()

  evaluateResponse(success, errors)
