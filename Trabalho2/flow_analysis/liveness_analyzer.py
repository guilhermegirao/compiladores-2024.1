class LivenessAnalyzer:
  def __init__(self, filename):
    self.blocks = {}  # Armazena os blocos de código
    self.blocks_use_def = {}  # Armazena as variáveis usadas e definidas em cada bloco
    self.blocks_in_out = {}  # Armazena os conjuntos IN e OUT para cada bloco
    self.filename = filename

  def parse_blocks(self):
    # Lê o arquivo de entrada e extrai os blocos de código
    with open(self.filename, 'r') as file:
      while True:
        block_lines = []
        line = file.readline()
        if line == '':
          break
        block_info = line.split(' ')
        block_number = int(block_info[0])
        num_lines = int(block_info[1])
        for i in range(num_lines + 1):
          line_content = file.readline().rstrip(' \n')
          if i == num_lines:
            # Trata os sucessores do bloco
            successors = list(map(int, line_content.split(' ')))
            if successors == [0]:
              successors = [1]  # Se não há sucessores, considera o bloco 1 como sucessor
          else:
            block_lines.append(line_content)
        self.blocks[block_number] = (block_lines, successors)

  def calculate_use_def(self, block):
    # Calcula as variáveis usadas e definidas em um bloco
    block_lines, _ = block
    defs = []  # Lista para armazenar variáveis definidas
    uses = []  # Lista para armazenar variáveis usadas

    for line in block_lines:
      tokens = line.split(' ')  # Divide a linha em tokens

      # Remove palavras-chave que não são variáveis
      if 'return' in tokens:
        tokens.remove('return')
      if 'if' in tokens:
        tokens.remove('if')
        tokens.remove('goto')

      # Verifica se é uma atribuição (ex: x = y + z)
      if len(tokens) > 1 and tokens[1] == '=' and tokens[0] not in defs + uses:
        # Verifica se a variável sendo atribuída também é usada na expressão
        if tokens.count(tokens[0]) > 1:
          uses.append(tokens[0])
        else:
          defs.append(tokens[0])  # Adiciona a variável à lista de definições

        # Analisa o lado direito da atribuição
        for token in tokens[2:]:
          # Adiciona variáveis usadas que não foram definidas anteriormente
          if token not in defs + uses and token.isalnum() and not token.isdigit() and 'B' not in token:
            uses.append(token)
      else:
        # Para instruções que não são atribuições
        for token in tokens:
          # Adiciona variáveis usadas que não foram definidas anteriormente
          if token not in defs + uses and token.isalnum() and not token.isdigit() and 'B' not in token:
            uses.append(token)

    return uses, defs  # Retorna as listas de variáveis usadas e definidas

  def calculate_in_out(self):
    # Calcula os conjuntos IN e OUT para cada bloco
    while True:
      updated_in_out = {}
      for num in range(len(self.blocks), 0, -1):
        block = self.blocks.get(num)
        successors = block[1]
        use_def = self.blocks_use_def.get(num)
        defs = use_def[1]
        uses = use_def[0]
        out = []
        for succ in successors:
          out.extend(self.blocks_in_out.get(int(succ))[0])
        out = list(set(out))
        # Fórmula da análise de vivacidade: IN[B] = USE[B] ∪ (OUT[B] - DEF[B])
        in_set = list(set(uses + [var for var in out if var not in defs]))
        updated_in_out[num] = (in_set, out)
      if updated_in_out == self.blocks_in_out:
        break
      self.blocks_in_out = updated_in_out

  def analyze(self):
    # Realiza a análise de vivacidade
    self.parse_blocks()
    for block_number in range(1, len(self.blocks) + 1):
      block = self.blocks.get(block_number)
      self.blocks_in_out[block_number] = ([], [])
      self.blocks_use_def[block_number] = self.calculate_use_def(block)
    self.calculate_in_out()

  def print_results(self):
    for block_number in range(1, len(self.blocks) + 1):
      formatted_block = f'B{block_number}'
      use_def_n = self.blocks_use_def.get(block_number)
      in_out_n = self.blocks_in_out.get(block_number)

      print(formatted_block)
      print(f'│───def_{formatted_block} : {sorted(use_def_n[1])}')
      print(f'│───use_{formatted_block} : {sorted(use_def_n[0])}')
      print(f'│───IN[{formatted_block}] : {sorted(in_out_n[0])}')
      print(f'└───OUT[{formatted_block}]: {sorted(in_out_n[1])}')
      print()
