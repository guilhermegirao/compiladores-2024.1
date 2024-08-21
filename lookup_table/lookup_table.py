class LookupTable:
	def __init__(self):
		self.table = {}

	def add_variable(self, var_name, node):
		if var_name in self.table:
			return False

		self.table[var_name] = node
		return True

	def get_variable(self, var_name):
		return self.table.get(var_name)
