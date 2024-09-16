from flow_analysis.liveness_analyzer import LivenessAnalyzer
from flow_analysis.reaching_definitions_analyzer import ReachingDefinitionsAnalyzer
from flow_analysis.available_expressions_analyzer import AvailableExpressionsAnalyzer

INPUT_FILE = "./__tests__/input.txt"

if __name__ == "__main__":
  print()

  print("=== Questão 1 - Liveness Analysis:  ===")
  la = LivenessAnalyzer(INPUT_FILE)
  la.analyze()
  la.print_results()

  print("=== Questão 2 - Reaching Definitions: ===")
  rd = ReachingDefinitionsAnalyzer(INPUT_FILE)
  rd.analyze()
  rd.print_results()

  print("=== Questão 3 - Available Expressions: ===")
  ae = AvailableExpressionsAnalyzer(INPUT_FILE)
  ae.analyze()
  ae.print_results()
