#!/usr/bin/env python
import re

def _emph(m):
	return "\emph{" + m.group(1) + "}"
	
def _bold(m):
	return "\strong{" + m.group(1) + "}"

class MarkdownToLatex:
	def __init__(self):
		self.emph = re.compile('\*(.+)\*')
		self.bold = re.compile('\*\*(.+)\*\*')
		
	def _emphasise(self, text):
		lines = text.splitlines()
		result = []
		for line in lines:
			line = self.bold.sub(_bold, line)
			line = self.emph.sub(_emph, line)
			result.append(line)
		return '\n'.join(result)
		
if __name__ == "__main__":
	pass