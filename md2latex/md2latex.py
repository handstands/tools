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
	
def _footnote(m):
	return "\\footnote{" + m.group(1) + "}"

def _inline_image(m):
	result = '\\begin{figure}\n'
	result += '\includegraphics{%s}\n' % m.group('address')
	if m.group('title'):
		result += '\caption{%s}\n' % m.group('title')
	result += '\end{figure}'
	return result
	
def _inline_link(m):
	return '\href{%s}{%s}' % (m.group('address'), m.group('alt'))

class MarkdownToLatex:
	def __init__(self):
		self.emph = re.compile('\*(.+?)\*')
		self.bold = re.compile('\*\*(.+?)\*\*')
		self.chapter = re.compile('(.+)\n=+', re.MULTILINE)
		self.section = re.compile('(.+)\n\-+$', re.MULTILINE)
		self.atx = re.compile('(#+)(.+)')
		self.ul = re.compile('([\+\-\*])\s+(.+)')
		self.ol = re.compile('([0-9]+[0-9]*)\.\s+(.+)')
		self.footnote = re.compile('\^\((.+)\)')
		self.citation = re.compile('\[(\S+?)\]:\s+"(.+?)"\s+"(.+?)"\s+"(.+?)"')
		self.url = re.compile('\[(\S+?)\]:\s+\<?(\S+?)\>?\s+"(.+?)"')
		self.inline_reference = re.compile('(?P<image>\!)?\[(?P<alt>.+?)\]\s*\((?P<address>.+?)\s*(?:"(?P<title>.+?)")?\)')
		self.reference = re.compile('(?P<type>[\^\!])?\[(?P<ref>.+?)\]\[(?P<id>.*?)\]')
		
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
	
	def _footnotes(self, text):
		text = self.footnote.sub(_footnote, text)
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
				key, bib, long_entry, short_entry = citation.groups()
				if key in bibliography.keys():
					raise KeyError, "Duplicate key '%s'" % key
				bibliography[key] = (bib, long_entry, short_entry)
				line = self.citation.sub("", line)
			elif url:
				key, adress, link_text = url.groups()
				if key in urls.keys():
					raise KeyError, "Duplicate key '%s'" % key
				urls[key] = (adress, link_text)
				line = self.url.sub("", line)
			elif inline_reference:
				if inline_reference.group('image'):
					line = self.inline_reference.sub(_inline_image, line)
				else:
					line = self.inline_reference.sub(_inline_link, line)
			lines.append(line)
		result = []
		bib_tags = []
		for line in lines:
			reference = self.reference.search(line)
			if reference:
				if reference.group('type'):
					if reference.group('type') == '!':
						if reference.group('ref') not in urls.keys():
							raise KeyError, "reference '%s' undefined" % reference.group('ref')
						line = self.reference.sub(r'\\begin{figure}\n\includegraphics{%s}\n\caption{%s}\n\end{figure}' % urls[reference.group('ref')], line)
					elif reference.group('type') == '^':
						if reference.group('ref') not in bibliography.keys():
							raise KeyError, "reference '%s' undefined" % reference.group('ref')
						if reference.group('id'):
							if reference.group('id') not in ('long', 'short', 'bib'):
								raise KeyError, "erroneus key '%s'" % reference.group('id')
							elif reference.group('id') == 'long':
								key = 1
							elif reference.group('id') == 'short':
								key = 2
							elif reference.group('id') == 'bib':
								key = 0
							line = self.reference.sub(bibliography[reference.group('ref')][key], line)
						else:
							if reference.group('ref') not in bib_tags:
								bib_tags.append(reference.group('ref'))
								key = 1
							else:
								key = 2
							line = self.reference.sub(bibliography[reference.group('ref')][key], line)
				else:
					if reference.group('ref') not in urls.keys():
						raise KeyError, "reference '%s' undefined" % reference.group('ref')
					line = self.reference.sub("\href{%s}{%s}" % urls[reference.group('ref')] , line)
			result.append(line)
		return '\n'.join(result)
	
	def markdownify(self, text):
		text = self._headings(text)
		text = self._lists(text)
		text = self._footnotes(text)
		text = self._emphasise(text)
		text = self._references(text)
		return text
		
if __name__ == "__main__":
	f = open('example.md')
	d = f.read()
	f.close()
	print MarkdownToLatex().markdownify(d)