import re
from instruction_selector.node import Node
from typing import Dict, List, Tuple
from graphviz import Digraph

class Tree:
  TKN_PATTERN = r'(MOVE|MEM|\+|\-|\*|\/)' #Padrão de "tokens"
  NTKN_PATTERN = r'\(|\)|\,' #Padrão de "não-tokens" (TEMP, CONST, FP etc...)
  SERIALIZED_PATTERN = r'\w+|[^\s\w]' #Padrão de instruções no formato linear (forma serializada)

  def __init__(self):
    self.root = None #Raiz da arvore
    self.scopes = [] #Lista de tuplas que representa os escopos
    self.cost_table: Dict[Node, Dict[str, Tuple[int, List[str]]]] = {}

  def unserialize(self, input):
    elements = re.findall(self.SERIALIZED_PATTERN, input) # Transforma a entrada em um array de palavras e tokens
    return elements

  def get_tokens(self, input):
    tokens = re.findall(self.TKN_PATTERN, input) #Encontra os "tokens" (+, -, *, /, MEM, MOVE)
    return tokens

  def makeTree(self, input):
    txt = self.unserialize(input)
    tokens = self.get_tokens(input)

    currentDirection = "L" #Inicia construção da arvore pela esquerda
    previous = None #Marca o node anterior
    actual_node = None #Nó atual
    rawValue = None #Valor bruto (para casos de TEMP x ou CONST x)

    for i in range(len(txt)): #ITERANDO SOBRE A ENTRADA
      if (i < len(txt)):
        if(not re.match(self.NTKN_PATTERN, txt[i])): #Se for um não-token
          if (txt[i] == "CONST" or txt[i] == "TEMP"):
            # Essa parte junta valores como TEMP x ou CONST x
            if (not re.match(self.NTKN_PATTERN, txt[i+1])):
              txt[i] = txt[i] + " " + txt[i+1]
              rawValue = txt[i+1]
              txt.pop(i+1)
            else:
              rawValue = txt[i]

          actual_node = Node(txt[i])
          actual_node.rawValue = rawValue

          #Marca os escopos e os nodes passados
          if (len(self.scopes) == 0):
            self.root = actual_node
            previous = self.root

          #Marca o nó pai e diz onde inserir o nó atual (esquerda ou direita)
          elif(previous is not None):
            if(currentDirection == "R"):
              #depois de colocar um nó na direita volto a inserir nós a esquerda (padrão)
              self.scopes[-1].right = actual_node
              currentDirection = "L"
            elif(currentDirection == "L"):
              self.scopes[-1].left = actual_node

            previous = actual_node

          #Atualiza os escopos
          if (txt[i] in tokens):
            self.scopes.append(actual_node)

        elif(txt[i] == "("): pass #Parenteses a esquerda -> nada acontece
        elif(txt[i] == ")"):  #Parenteses a direita -> Volta ao escopo anterior
          self.scopes.pop()
          if (len(self.scopes) >= 1):
            previous = self.scopes[-1]
        elif(txt[i] == ","): #Virgula -> proximo nó está a direita
          currentDirection = "R"

  def generateTreeImage(self, filename="tree_graph"):
    dot = Digraph()

    def add_nodes_and_edges(node):
      if node:
        dot.node(str(id(node)), node.value)
        if node.left:
          dot.edge(str(id(node)), str(id(node.left)))
          add_nodes_and_edges(node.left)
        if node.right:
          dot.edge(str(id(node)), str(id(node.right)))
          add_nodes_and_edges(node.right)

    if self.root:
      add_nodes_and_edges(self.root)

    dot.render(filename, format="png")
