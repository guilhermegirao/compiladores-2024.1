from semantic_analyzer import SemanticAnalyzer

def evaluateResponse(success):
  return "Sucesso" if success else "Falha"

def evaluateErrors(errors):
  for error in errors:
    print(error)

if __name__ == "__main__":
  source_code = """
  int a = 1;
  string b = 2;
  int c = a + b;

  """

#falta fazer validação de caracteres que não existem na linguagem na expressão
#fazer validação de outros problemas listados tipo int a; int b; int c = a +b; (ok)
#criar erros gericos tipo i18n
#colocar comentarios nas funções
#criar testes e fazer a main rodar
#substituir valores fixos pelos literals
#perguntar pro professor se existe operação de concatenação em string, pois no c não tem
  analyzer = SemanticAnalyzer()
  analyzer.parse_and_analyze(source_code)
  success, errors = analyzer.response()

  print(evaluateResponse(success))
  print(errors)