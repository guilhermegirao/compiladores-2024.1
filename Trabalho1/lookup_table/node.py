# Node para a lookup table
class Node:
	def __init__(self, name, var_type=None, value=None):
		self.name = name
		self.var_type = var_type
		self.value = value

	def update(self, var_type, value):
		self.var_type = var_type
		self.value = value
