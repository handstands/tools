#!/usr/bin/env python3
"""MarkdownToLatex provides a class to easily convert Markdown to LaTeX-syntax"""
import re
import argparse
import os.path

def _atx(matches):
	"""_atx takes care of ATX-style headings"""
	heading_level = len(matches.group('hashes'))
	title = matches.group('title').replace('#', '').strip()
	if heading_level == 1:
		return "\\chapter{" + title + "}"
	elif heading_level == 2:
		return "\\section{" + title + "}"
	elif heading_level == 3:
		return "\\subsection{" + title + "}"
	else:
		return "\\subsubsection{" + title + "}"

def _inline_image(matches):
	"""_inline_image takes care of images"""
	result = '\\begin{figure}\n'
	result += '\\includegraphics{%s}\n' % matches.group('address')
	if matches.group('title'):
		result += '\\caption{%s}\n' % matches.group('title')
	result += '\\end{figure}'
	return result

class MarkdownToLatex:
	"""MarkdownToLatex provides the means to convert Markdown-documents to LaTeX"""
	def __init__(self):
		self.emph = re.compile(r'((?<!\\)[\*_])(?P<text>[^\\].*?)(\1)')
		self.bold = re.compile(r'((\\{0}[\*_]){2})(?P<text>.+?)\1')
		self.monospace = re.compile('`(?P<text>.+?)`')
		self.chapter = re.compile('(?P<title>.+)\n=+', re.MULTILINE)
		self.section = re.compile(r'(?P<title>.+)\n\-+$', re.MULTILINE)
		self.atx = re.compile('(?P<hashes>#+)(?P<title>.+)')
		self.unordered = re.compile(r'^\s*([\+\-\*])\s+(?P<text>.+)')
		self.ordered = re.compile(r'^\s*([1-9]+[0-9]*)\.\s+(?P<text>.+)')
		self.footnote = re.compile(r'\^\((?P<text>.+)\)')
		self.citation = re.compile(r'\[(?P<ref>\S+?)\]:\s+"(?P<bib>.+?)"\s+"(?P<long>.+?)"\s+"(?P<short>.+?)"')
		self.url = re.compile(r'\[(?P<ref>\S+?)\]:\s+\<?(?P<url>\S+?)\>?\s+"(?P<desc>.+?)"')
		self.inline_reference = re.compile(r'(?P<image>\!)?\[(?P<alt>.+?)\]\s*\((?P<address>.+?)\s*(?:"(?P<title>.+?)")?\)')
		self.reference = re.compile(r'(?P<type>[\^\!])?\[(?P<ref>.+?)\]\[(?P<id>.*?)\]')
		self.quote = re.compile(r'\s*>\s+(?P<text>.+)')

	def _emphasise(self, text):
		"""_emphasise takes care of emphasis and bolding"""
		text = self.bold.sub(lambda m: "\\textbf{%s}" % m.group('text'), text)
		text = self.emph.sub(lambda m: "\\emph{%s}" % m.group('text'), text)
		text = self.monospace.sub(lambda m: "\\texttt{%s}" % m.group('text'), text)
		return text

	def _headings(self, text):
		"""_headings takes care of headings"""
		text = self.chapter.sub(lambda m: "\\chapter{%s}" % m.group('title').strip(), text)
		text = self.section.sub(lambda m: "\\section{%s}" % m.group('title').strip(), text)
		text = self.atx.sub(_atx, text)
		return text

	def _lists(self, text):
		"""_lists takes care of lists"""
		result = []
		active_list = ""
		begin = {'ordered': r'\begin{enumerate}', 'unordered': r'\begin{itemize}'}
		end = {'ordered': r'\end{enumerate}', 'unordered': r'\end{itemize}'}
		for line in text.splitlines():
			unordered = self.unordered.search(line)
			ordered = self.ordered.search(line)
			if unordered or ordered:
				if not active_list:
					if unordered:
						active_list = 'unordered'
					elif ordered:
						active_list = 'ordered'
					result.append(begin[active_list])
				if unordered:
					result.append(self.unordered.sub(lambda m: "\\item %s" % m.group('text').strip(), line))
				elif ordered:
					result.append(self.ordered.sub(lambda m: "\\item %s" % m.group('text').strip(), line))

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
		"""_footnotes takes care of footnotes"""
		text = self.footnote.sub(lambda m: "\\footnote{%s}" % m.group('text'), text)
		return text

	def _references(self, text):
		"""_references takes care of embedded bibliography and references"""
		bibliography = {}
		urls = {}
		#image = {}
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
					line = self.inline_reference.sub(lambda m: '\\href{%s}{%s}' % (m.group('address'), m.group('alt')), line)
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
					line = self.reference.sub(r"\\href{%s}{%s}" % urls[reference.group('ref')], line)
			result.append(line)
		return '\n'.join(result)

	def _quotes(self, text):
		"""_quotes taks care of quotation blocks"""
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
					results.append('\\end{quote}')
					active_block = False
			results.append(line)
		if active_block:
			results.append('\\end{quote}')
		return '\n'.join(results)

	def markdownify(self, text):
		"""markdownify markdownifies the input text"""
		text = self._headings(text)
		text = self._lists(text)
		text = self._footnotes(text)
		text = self._emphasise(text)
		text = self._references(text)
		return text

	def markdown_file(self, file):
		"""markdownFile markdownifies an input file"""
		with open(file) as md_file:
			markdown_text = md_file.read()
		return self.markdownify(markdown_text)
#		return md

	def markdown_template(self, markdown_file, template):
		"""markdownWithTemplate converts a Markdown-file to LaTeX and embeds it into a template file"""
		with open(template) as temp_file:
			temp = temp_file.read()
		markdown_text = self.markdown_file(markdown_file)
		rep = r'%BODY%'
		print(rep)
		temp = temp.replace(rep, markdown_text)
		return temp

if __name__ == "__main__":
	PARSER = argparse.ArgumentParser(description='This is a script designed to convert a file with Markdown-style formatting into a comparable LaTeX file.')
	PARSER.add_argument('-i', '--input-file', help='Markdown-style file to be converted.', required=True)
	PARSER.add_argument('-o', '--output-file', help='File where the generated LaTeX code will be written to. If not, the script will output to stdout.', required=False, default="")
	PARSER.add_argument('-t', '--template', help=r'Template file. If set, the script will attempt to replace the \%BODY\% with the LaTeX code generated by the script.', required=False, default='')
	#with open('example.md') as f:
	#	d = f.read()
	#print(MarkdownToLatex().markdownify(d))
	ARGS = vars(PARSER.parse_args())
	if not os.path.exists(ARGS['input_file']):
		print("Input file '%s' not found" % ARGS['input_file'])
		exit()
	if ARGS['template']:
		if not os.path.exists(ARGS['template']):
			print("Template file '%s' not found" % ARGS['template'])
			exit()
		OUTPUT = MarkdownToLatex().markdown_template(ARGS['input_file'], ARGS['template'])
	else:
		OUTPUT = MarkdownToLatex().markdown_file(ARGS['input_file'])

	if ARGS['output_file']:
		with open(ARGS['output_file'], 'w') as f:
			f.write(OUTPUT)
	else:
		print(OUTPUT)
		