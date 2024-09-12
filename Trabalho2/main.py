import os
from instruction_selector.selector import Selector
from instruction_selector.tree import Tree

input_path = "./__tests__"

if __name__ == "__main__":
  # Para testes com todos os inputs dentro da pasta /__tests__
  for file in os.listdir(input_path):
    if file.endswith(".txt"):
      path = f"{input_path}/{file}"
      with open(path, encoding='utf8') as f:
        instructions = f.read()

      print("=== ARQUIVO:", file, " ===")
      t = Tree()
      t.makeTree(instructions) #Cria arvore

      tree_name = f'__outputs__/tree_graph/{file}'.replace('.txt', '')
      t.generateTreeImage(tree_name)
      os.remove(tree_name) # Remove o arquivo dot gerado pelo graphviz

      print(f"=== ARVORE GRAFICAMENTE SALVA EM: {tree_name}.png")

      print('\n')
      s = Selector(t) #Cria o seletor, que já irá fazer a seleção
      print("=== PADRÕES SELECIONADOS:")
      t.printTiles() #Imprime os padrões (optimal tiling)
      print('\n')
      print("=== INSTRUÇÕES SELECIONADAS:")
      s.printInstructions(t.getPatterns()) #Imprime as instruções baseando-se nos padrões
      print('\n')
