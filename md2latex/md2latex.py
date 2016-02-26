#!/usr/bin/env python
import re

def _emph(m):
	return "\emph{" + m.group(1) + "}"
	
def _bold(m):
	return "\strong{" + m.group(1) + "}"
	
def _chapter(m):
	return "\chapter{" + m.group(1).strip() + "}"
	
def _section(m):
	return "\section{" + m.group(1).strip() + "}"
	
def _atx(m):
	heading_level = len(m.group(1))
	title = m.group(2).replace('#', '').strip()
	if heading_level == 1:
		return "\chapter{" + title + "}"
	elif heading_level == 2:
		return "\section{" + title + "}"
	elif heading_level == 3:
		return "\subsection{" + title + "}"
	else:
		return "\subsubsection{" + title + "}"

class MarkdownToLatex:
	def __init__(self):
		self.emph = re.compile('\*(.+)\*')
		self.bold = re.compile('\*\*(.+)\*\*')
		self.chapter = re.compile('(.+)\n=+', re.MULTILINE)
		self.section = re.compile('(.+)\n\-+', re.MULTILINE)
		self.atx = re.compile('(#+)(.+)')
		
	def _emphasise(self, text):
		lines = text.splitlines()
		result = []
		for line in lines:
			line = self.bold.sub(_bold, line)
			line = self.emph.sub(_emph, line)
			result.append(line)
		return '\n'.join(result)
	
	def _headings(self, text):
		text = self.chapter.sub(_chapter, text)
		text = self.section.sub(_section, text)
		text = self.atx.sub(_atx, text)
		return text
		
if __name__ == "__main__":
	print MarkdownToLatex()._headings("Test\n====")
	print MarkdownToLatex()._headings("Test\n----")
	print MarkdownToLatex()._headings("##### Test #####")