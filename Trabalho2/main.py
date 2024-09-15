import os
# from instruction_selector.selector import Selector
from instruction_selector.tree import Tree

def format_file_name(file):
  return file.replace('.txt', '')

input_path = "./__tests__"

if __name__ == "__main__":
  # Para testes com todos os inputs dentro da pasta /__tests__
  for file in os.listdir(input_path):
    if file.endswith(".txt"):
      with open(f"{input_path}/{file}", encoding='utf8') as f:
        instructions = f.read()

      print(f"* TESTE {format_file_name(file)}:")

      t = Tree()
      t.makeTree(instructions) #Cria arvore

      tree_name = format_file_name(f'__outputs__/tree_graph/{file}')
      t.generateTreeImage(tree_name)
      os.remove(tree_name) # Remove o arquivo dot gerado pelo graphviz

      print(f"=== ARVORE GRAFICAMENTE SALVA EM: {tree_name}.png")
      print('\n')

      print("=== PADRÕES SELECIONADOS:")

      print("=== INSTRUÇÕES SELECIONADAS:")

      print('\n')
