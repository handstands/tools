#!/usr/bin/env python3
import re

def _atx(m):
	heading_level = len(m.group('hashes'))
	title = m.group('title').replace('#', '').strip()
	if heading_level == 1:
		return "\chapter{" + title + "}"
	elif heading_level == 2:
		return "\section{" + title + "}"
	elif heading_level == 3:
		return "\subsection{" + title + "}"
	else:
		return "\subsubsection{" + title + "}"

def _inline_image(m):
	result = '\\begin{figure}\n'
	result += '\includegraphics{%s}\n' % m.group('address')
	if m.group('title'):
		result += '\caption{%s}\n' % m.group('title')
	result += '\end{figure}'
	return result
	
class MarkdownToLatex:
	def __init__(self):
		self.emph = re.compile(r'((?<!\\)[\*_])(?P<text>[^\\].*?)(\1)')
		self.bold = re.compile(r'((\\{0}[\*_]){2})(?P<text>.+?)\1')
		self.monospace = re.compile('`(?P<text>.+?)`')
		self.chapter = re.compile('(?P<title>.+)\n=+', re.MULTILINE)
		self.section = re.compile('(?P<title>.+)\n\-+$', re.MULTILINE)
		self.atx = re.compile('(?P<hashes>#+)(?P<title>.+)')
		self.ul = re.compile('^\s*([\+\-\*])\s+(?P<text>.+)')
		self.ol = re.compile('^\s*([1-9]+[0-9]*)\.\s+(?P<text>.+)')
		self.footnote = re.compile('\^\((?P<text>.+)\)')
		self.citation = re.compile('\[(?P<ref>\S+?)\]:\s+"(?P<bib>.+?)"\s+"(?P<long>.+?)"\s+"(?P<short>.+?)"')
		self.url = re.compile('\[(?P<ref>\S+?)\]:\s+\<?(?P<url>\S+?)\>?\s+"(?P<desc>.+?)"')
		self.inline_reference = re.compile('(?P<image>\!)?\[(?P<alt>.+?)\]\s*\((?P<address>.+?)\s*(?:"(?P<title>.+?)")?\)')
		self.reference = re.compile('(?P<type>[\^\!])?\[(?P<ref>.+?)\]\[(?P<id>.*?)\]')
		self.quote = re.compile('\s*>\s+(?P<text>.+)')
		
	def _emphasise(self, text):
		text = self.bold.sub(lambda m: "\\strong{%s}" % m.group('text'), text)
		text = self.emph.sub(lambda m: "\\emph{%s}" % m.group('text'), text)
		text = self.monospace.sub(lambda m: "\\texttt{%s}" % m.group('text'), text)
		return text
	
	def _headings(self, text):
		text = self.chapter.sub(lambda m: "\chapter{%s}" % m.group('title').strip(), text)
		text = self.section.sub(lambda m: "\section{%s}" % m.group('title').strip(), text)
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
					result.append(self.ul.sub(lambda m: "\item %s" % m.group('text').strip(), line))
				elif ordered:
					result.append(self.ol.sub(lambda m: "\item %s" % m.group('text').strip(), line))
					
			elif line.startswith("\t"):
				result[-1] += " " + line[1:]
			elif line.startswith("    "):
				result[-1] += line[3:]
			elif line == "":
				result[-1] += "\\\\"
			else:
				if active_list:
					result.append(end[active_list])
				active_list = ""
				result.append(line)
		if active_list:
			result.append(end[active_list])
		return '\n'.join(result)
	
	def _footnotes(self, text):
		text = self.footnote.sub(lambda m: "\\footnote{%s}" % m.group('text'), text)
		return text
		
	def _references(self, text):
		bibliography = {}
		urls = {}
		image = {}
		lines = []
		for line in text.splitlines():
			citation = self.citation.search(line)
			url = self.url.search(line)
			inline_reference = self.inline_reference.search(line)
			if citation:
				if citation.group('ref') in bibliography.keys():
					raise KeyError("Duplicate key '%s'" % citation.group('ref'))
				bibliography[citation.group('ref')] = {'bib': citation.group('bib'), 'long': citation.group('long'), 'short': citation.group('short')}
				line = self.citation.sub("", line)
			elif url:
				if url.group('ref') in urls.keys():
					raise KeyError("Duplicate key '%s'" % url.group('ref'))
				urls[url.group('ref')] = (url.group('url'), url.group('desc'))
				line = self.url.sub("", line)
			elif inline_reference:
				if inline_reference.group('image'):
					line = self.inline_reference.sub(_inline_image, line)
				else:
					line = self.inline_reference.sub(lambda m: '\href{%s}{%s}' % (m.group('address'), m.group('alt')), line)
			lines.append(line)
		result = []
		bib_tags = []
		for line in lines:
			reference = self.reference.search(line)
			if reference:
				if reference.group('type'):
					if reference.group('type') == '!':
						if reference.group('ref') not in urls.keys():
							raise KeyError("reference '%s' undefined" % reference.group('ref'))
						line = self.reference.sub(r'\\begin{figure}\n\\includegraphics{%s}\n\\caption{%s}\n\\end{figure}' % urls[reference.group('ref')], line)
					elif reference.group('type') == '^':
						if reference.group('ref') not in bibliography.keys():
							raise KeyError("reference '%s' undefined" % reference.group('ref'))
						if reference.group('id'):
							if reference.group('id') not in ('long', 'short', 'bib'):
								raise KeyError("erroneus key '%s'" % reference.group('id'))
							line = self.reference.sub(bibliography[reference.group('ref')][reference.group('id')], line)
						else:
							if reference.group('ref') not in bib_tags:
								bib_tags.append(reference.group('ref'))
								key = 'long'
							else:
								key = 'short'
							line = self.reference.sub(bibliography[reference.group('ref')][key], line)
				else:
					if reference.group('ref') not in urls.keys():
						raise KeyError("reference '%s' undefined" % reference.group('ref'))
					line = self.reference.sub(r"\\href{%s}{%s}" % urls[reference.group('ref')] , line)
			result.append(line)
		return '\n'.join(result)

	def _quotes(self, text):
		results = []
		active_block = False
		for line in text.splitlines():
			quote = self.quote.search(line)
			if quote:
				if not active_block:
					results.append('\\begin{quote}')
					active_block = True
				line = self.quote.sub(lambda m: m.group('text'), line)
			else:
				if active_block:
					results.append('\end{quote}')
					active_block = False
			results.append(line)
		if active_block:
			results.append('\end{quote}')
		return '\n'.join(results)
	
	def markdownify(self, text):
		text = self._headings(text)
		text = self._lists(text)
		text = self._footnotes(text)
		text = self._emphasise(text)
		text = self._references(text)
		return text
		
if __name__ == "__main__":
	with open('example.md') as f:
		d = f.read()
	print(MarkdownToLatex().markdownify(d))