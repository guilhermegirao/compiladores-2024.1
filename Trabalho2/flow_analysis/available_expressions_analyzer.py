import pandas as pd

class AvailableExpressionsAnalyzer:
  def __init__(self, input_file):
    self.blocks = {}  # Armazena os blocos de código
    self.blocks_expr = {}  # Armazena as expressões em cada bloco
    self.prev_block = {1: []}  # Armazena os predecessores de cada bloco
    self.gen_kill = {}  # Armazena os conjuntos GEN e KILL para cada bloco
    self.in_out = {}  # Armazena os conjuntos IN e OUT para cada bloco
    self.end_blocks = []  # Lista de blocos finais
    self.all_expr = []  # Todas as expressões no programa
    self.input_file = input_file

  def parse_blocks(self):
    # Lê o arquivo de entrada e extrai os blocos de código e expressões
    with open(self.input_file, 'r') as file:
      while True:
        block_expr = []
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
            if max(successors) <= block_number:
              self.end_blocks.append(block_number)
            for succ in [x for x in successors if x != 0]:
              if succ in self.prev_block:
                self.prev_block[succ].append(block_number)
              else:
                self.prev_block[succ] = [block_number]
          else:
            block_lines.append(line_content)
            # Extrai expressões do lado direito das atribuições
            expr = line_content.split(' = ')[1]
            expr_vars = expr.split(' ')
            if any(var.isalnum() and not var.isdigit() for var in expr_vars):
              block_expr.append(expr)
              self.all_expr.append(expr)
        self.blocks_expr[block_number] = block_expr
        self.blocks[block_number] = (block_lines, successors)

    # Atualiza a lista de predecessores para o bloco de entrada
    entry_block_successors = self.prev_block.get(1)
    entry_block_successors.extend(self.end_blocks)
    self.prev_block[1] = entry_block_successors
    self.all_expr = list(set(self.all_expr))

  def calculate_gen_kill(self, block, block_expr):
    # Calcula os conjuntos GEN e KILL para um bloco
    block_lines, _ = block
    gen = []
    kill = []
    for index, expr in enumerate(block_expr):
      is_live = True
      for line in block_lines[index:]:
        line_var, line_expr = line.split(' = ')
        if line_var in expr:
          is_live = False
        if line_expr == expr:
          is_live = True
      if is_live:
        gen.append(expr)
      else:
        kill.append(expr)
    return gen, kill

  def calculate_in_out(self):
    # Calcula os conjuntos IN e OUT para cada bloco
    while True:
      updated_in_out = {}
      for num in range(1, len(self.blocks) + 1):
        gen_kill_data = self.gen_kill.get(num)
        gen = gen_kill_data[0]
        kill = gen_kill_data[1]
        predecessors = self.prev_block.get(num)
        in_set = []
        for pred in predecessors:
          in_set.extend(self.in_out.get(pred)[1])
        # Fórmula para expressões disponíveis: IN[B] = ∩ OUT[P] para todos os predecessores P de B
        in_set = list({x for x in in_set if in_set.count(x) == len(predecessors)})
        # Fórmula para expressões disponíveis: OUT[B] = GEN[B] ∪ (IN[B] - KILL[B])
        out_set = list(set(gen + [x for x in in_set if x not in kill]))
        updated_in_out[num] = (in_set, out_set)
      if updated_in_out == self.in_out:
        break
      self.in_out = updated_in_out

  def analyze(self):
    # Realiza a análise de expressões disponíveis
    self.parse_blocks()
    for num in range(1, len(self.blocks) + 1):
      block = self.blocks.get(num)
      block_expr = self.blocks_expr.get(num)
      self.gen_kill[num] = self.calculate_gen_kill(block, block_expr)
      block_kill = self.gen_kill.get(num)[1]
      self.in_out[num] = ([], [e for e in self.all_expr if e not in block_kill])

    self.calculate_in_out()

  def print_results(self):
    for num in self.blocks:
      formatted_block = f'B{num}'
      gen_kill_data = self.gen_kill.get(num)
      in_out_data = self.in_out.get(num)

      print(formatted_block)
      print(f'│───gen_{formatted_block} : {sorted(gen_kill_data[0])}')
      print(f'│───kill_{formatted_block}: {sorted(gen_kill_data[1])}')
      print(f'│───IN[{formatted_block}] : {sorted(in_out_data[0])}')
      print(f'└───OUT[{formatted_block}]: {sorted(in_out_data[1])}')
      print()