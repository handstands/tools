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

def _ul(m):
	return "\item " + m.group(2).strip()

class MarkdownToLatex:
	def __init__(self):
		self.emph = re.compile('\*(.+?)\*')
		self.bold = re.compile('\*\*(.+?)\*\*')
		self.chapter = re.compile('(.+)\n=+', re.MULTILINE)
		self.section = re.compile('(.+)\n\-+', re.MULTILINE)
		self.atx = re.compile('(#+)(.+)')
		self.ul = re.compile('([\+\-\*])\s+(.+)')
		self.ol = re.compile('([0-9]+[0-9]*)\.\s+(.+)')
		
	def _emphasise(self, text):
		text = self.bold.sub(_bold, text)
		text = self.emph.sub(_emph, text)
		return text
	
	def _headings(self, text):
		text = self.chapter.sub(_chapter, text)
		text = self.section.sub(_section, text)
		text = self.atx.sub(_atx, text)
		return text
		
	def _lists(self, text):
		result = []
		active_list = ""
		begin = {'ordered': r'\begin{enumerate}', 'unordered': r'\begin{itemize}'}
		end = {'ordered': r'\end{enumerate}', 'unordered': r'\end{itemize}'}
		for line in text.splitlines():
			unordered = self.ul.search(line)
			ordered = self.ol.search(line)
			if unordered or ordered:
				if not active_list:
					if unordered:
						active_list = 'unordered'
					elif ordered:
						active_list = 'ordered'
					result.append(begin[active_list])
				if unordered:
					result.append(self.ul.sub(_ul, line))
				elif ordered:
					result.append(self.ol.sub(_ul, line))
			else:
				if active_list:
					result.append(end[active_list])
				active_list = ""
				result.append(line)
		if active_list:
			result.append(end[active_list])
		return '\n'.join(result)
		
if __name__ == "__main__":
	print MarkdownToLatex()._headings("Test\n====")
	print MarkdownToLatex()._headings("Test\n----")
	print MarkdownToLatex()._headings("##### Test #####")
	print MarkdownToLatex()._emphasise("*a* *b* **c** **d**")
	print MarkdownToLatex()._emphasise("Like fucking *emphasise* this un**fucking**believable\n*story*")
	print MarkdownToLatex()._lists("* abc\n * fde\n * ijk")
	print MarkdownToLatex()._lists("1. abc\n 2. fde\n 3. ijk\n\n* foo\n* bar\n* baz")