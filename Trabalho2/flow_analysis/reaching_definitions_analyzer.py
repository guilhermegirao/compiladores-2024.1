from collections import defaultdict

class ReachingDefinitionsAnalyzer:
  def __init__(self, filename):
    self.filename = filename
    self.def_num = 1  # Contador para identificar definições
    self.defs = {}  # Dicionário que armazena as definições
    self.vars_defs = defaultdict(list)  # Armazena quais variáveis estão associadas a quais definições
    self.in_out = {}  # Armazena os conjuntos de entrada e saída de definições para cada bloco
    self.gens_kills = {}  # Armazena os conjuntos de gen (gera) e kill (mata) para cada bloco
    self.blocks = {}  # Dicionário que armazena os blocos de código
    self.prev_block = defaultdict(list)  # Dicionário que armazena os predecessores de cada bloco
    self.end_blocks = []  # Lista de blocos finais (blocos que não têm sucessores)

  def parse_input(self):
    # Abre o arquivo de entrada contendo os blocos de código
    try:
      with open(self.filename, 'r') as f:
        while True:
          line = f.readline()
          if line == '':
            break

          line = line.split()
          block_num = int(line[0])
          block_n_lines = int(line[1])
          block = []

          for i in range(block_n_lines + 1):
            aux = next(f).rstrip(' \n')

            if i == block_n_lines:
              ver = [int(x) for x in aux.split()]

              # Se o maior sucessor for menor ou igual ao número do bloco, é um bloco final
              if max(ver) <= block_num:
                self.end_blocks.append(block_num)

              # Adiciona o bloco atual como sucessor dos predecessores
              for v in [x for x in ver if x != 0]:
                self.prev_block[v].append(block_num)

            else:
              # Armazena a definição no bloco
              block.append(f'd{self.def_num}: {aux}')
              self.defs[f'd{self.def_num}'] = aux
              var = aux.split(' = ')[0]

              # Atualiza o dicionário de variáveis e suas definições
              self.vars_defs[var].append(f'd{self.def_num}')

              self.def_num += 1

          self.blocks[block_num] = (block, ver)

    except FileNotFoundError:
      print(f"Error: File '{self.filename}' not found.")
      exit(1)

    # Conecta os blocos finais aos predecessores do bloco 1
    self.prev_block[1].extend(self.end_blocks)

  # Função para calcular os conjuntos gen (gera) e kill (mata) de um bloco
  def get_gen_kill(self, bl):
    gen = []
    kill = []
    bl_lines = bl[0]

    for lin in bl_lines:
      lin = lin.split(': ')
      line_def = lin[0]
      gen.append(line_def)

      line_var = lin[1].split(' = ')[0]
      list_aux = self.vars_defs.get(line_var, [])
      line_var_defs = list_aux[:]
      line_var_defs.remove(line_def)

      for df in line_var_defs:
        kill.append(df)

    return gen, list(set(kill))

  # Função para calcular os conjuntos de entrada e saída para cada bloco
  def calculate_in_out(self):
    dict_aux = {}

    while True:
      for num in range(1, len(self.blocks) + 1):
        b_gen_kill = self.gens_kills.get(num)
        b_gen = b_gen_kill[0]
        b_kill = b_gen_kill[1]
        b_prev = self.prev_block.get(num, [])
        b_in = []

        # Coleta as entradas dos blocos predecessores
        for v in b_prev:
          if v in dict_aux:
            b_in.extend(dict_aux.get(int(v))[1])

        b_in = list(set(b_in))
        # Define o conjunto de saída
        b_out = list(set(b_gen + [x for x in b_in if x not in b_kill]))
        dict_aux[num] = (b_in, b_out)

      # Verifica se o conjunto de entrada/saída estabilizou
      if dict_aux == self.in_out:
        break

      self.in_out = dict_aux

  def analyze(self):
    self.parse_input()

    # Calcula os conjuntos de gen/kill para cada bloco
    for n in range(1, len(self.blocks) + 1):
      b = self.blocks.get(n)
      self.in_out[n] = ([], [])
      self.gens_kills[n] = self.get_gen_kill(b)

    # Calcula os conjuntos de entrada e saída para todos os blocos
    self.calculate_in_out()

  def print_results(self):
    for n in self.blocks:
      formatted_block = f'B{n}'
      gens_kills_n = self.gens_kills.get(n)
      in_out_n = self.in_out.get(n)

      print(formatted_block)
      print(f'│───gen_{formatted_block} : {sorted(gens_kills_n[0])}')
      print(f'│───kill_{formatted_block}: {sorted(gens_kills_n[1])}')
      print(f'│───IN[{formatted_block}] : {sorted(in_out_n[0])}')
      print(f'└───OUT[{formatted_block}]: {sorted(in_out_n[1])}')
      print()
