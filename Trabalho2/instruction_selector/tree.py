import re
from instruction_selector.node import Node
from graphviz import Digraph

class Tree():
  TKN_PATTERN = r'(MOVE|MEM|\+|\-|\*|\/)' #Padrão de "tokens"
  NTKN_PATTERN = r'\(|\)|\,' #Padrão de "não tokens" (TEMP, CONST e outros valores como FP etc...)

  def __init__(self): 
    self.root = None #Raiz da arvore
    self.scopes = [] #Lista de tuplas que representa os escopos

  def makeTree(self, str):
    txt = str.split() #Divide o input em espaços em branco
    tokens = re.findall(self.TKN_PATTERN, str) #Encontra os "tokens" (+, -, *, /, MEM, MOVE)
    currentDirection = "L" #Inicia construção da arvore pela esquerda
    previous = None #Marca o node anterior
    aux = None #Nó atual
    self.node_path = [] #Enquanto construo a arvore eu faço um array do "caminho" da arvore que vai ser util mais na frente
    rawValue = None #Valor bruto (para casos de TEMP x ou CONST x)
    for i in range(len(txt)): #ITERANDO SOBRE A ENTRADA
      if (i < len(txt)):
        if(not re.match(self.NTKN_PATTERN, txt[i])): #Se for um não token
          if (txt[i] == "CONST" or txt[i] == "TEMP"):
            #Essa parte junta valores como TEMP x ou CONST x
            if (not re.match(self.NTKN_PATTERN, txt[i+1])):
              txt[i] = txt[i] + " " + txt[i+1]
              rawValue = txt[i+1]
              txt.pop(i+1)
            else:
              rawValue = txt[i]

          aux = Node(txt[i])
          aux.rawValue = rawValue

          #Marca os escopos e os nodes passados
          if (len(self.scopes) == 0):
            self.root = aux
            self.node_path.append(self.root)
            previous = self.root

          #Marca o nó pai e diz onde inserir o nó atual (esquerda ou direita)
          elif(previous is not None):
            aux.father = self.scopes[-1]
            if(currentDirection == "R"):
              #depois de colocar um nó na direita volto a inserir nós a esquerda (padrão)
              self.scopes[-1].right = aux
              currentDirection = "L"
            elif(currentDirection == "L"):
              self.scopes[-1].left = aux

            self.node_path.append(aux)
            previous = aux

          #Atualiza os escopos
          if (txt[i] in tokens):
            self.scopes.append(aux)

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

  #Printa os padrões (tile)
  def printTiles(self):
    tiles = []
    for n in self.node_path:
      if(n.isUsed):
        tiles.append(self.getTileVal(n.selectedTile))

    print('\n'.join([' ==> '.join([str(cell) for cell in row]) for row in tiles]))
    self.calculateCost(tiles)

  #Função auxiliar para obter os valores dos nos de um padrão (tile)
  def getTileVal(self, tile):
    tile_v = []
    for t in tile:
      tile_v.append(t.value)
    return tile_v

  #Função para calcular o custo da arvore
  def calculateCost(self, tileArray):
    cost = 0
    for tile in tileArray:
      if (tile[0] == "MOVE"): #CASO MOVE
        if(tile == ["MOVE", "MEM", "MEM"]): #Se o padrão for MOVE, MEM, MEM indica um MOVEM e o custo é somado em 2
          cost += 2
        else: cost += 1 #Do contrário o custo é 1
      elif(re.match(r'CONST.*?', tile[0])): #CASO CONST
        cost += 1
      elif(tile[0] in ["+", "-", "*", "/", "MEM"]): #CASO Operações básicas
        cost += 1

    #CASO TEMP ou outro registrador como FP, não têm custo

    print("=== CUSTO TOTAL: ", cost, " ===")

  #Pega os padrões no formato (node, numero_padrão)
  def getPatterns(self):
    res = []
    for n in self.node_path: #Verifica os nós utilizados, ou seja, as raizes dos padrões
      if(n.isUsed):
        res.append([n, n.pattern])

    return res
