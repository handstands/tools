#!/usr/bin/env python
from md2latex import MarkdownToLatex
import unittest

class Emphasis(unittest.TestCase):
	def testBasicEmphasis(self):
		"""_emphasise should emphasise strings between two *"""
		result = MarkdownToLatex()._emphasise("*emphasis*")
		self.assertEqual(result, "\emph{emphasis}")
		
	def testEscapedAsterisks(self):
		"""_emphasise should not emphasise if the asterisk is escaped"""
		result = MarkdownToLatex()._emphasise("\*emphasis")
		self.assertEqual(result, "\*emphasis")
		
	def testSkipsLists(self):
		"""_emphasise should skip list items that are preceded by an asterisk and separated from the rest by a space"""
		result = MarkdownToLatex()._emphasise("* list item")
		self.assertEqual(result, "* list item")
		
	def testBalance(self):
		"""_emphasise should only emphasise the string encapsulated between two *"""
		resulta = MarkdownToLatex()._emphasise("*not emphasised")
		resultb = MarkdownToLatex()._emphasise("**not bolded")
		self.assertEqual(resulta, "*not emphasised")
		self.assertEqual(resultb, "**not bolded")
		
	def testDoubleEmphasis(self):
		"""_emphasise should bold text between double asterisks"""
		result = MarkdownToLatex()._emphasise("**bolded**")
		self.assertEqual(result, "\strong{bolded}")
	
	def testMultipleEmphasised(self):
		tests = [("*a* *b*", "\emph{a} \emph{b}"), ("**a** **b**", "\strong{a} \strong{b}"), ("*a* **b**", "\emph{a} \strong{b}"), ("**a** *b*", "\strong{a} \emph{b}")]
		"""_emphasise should emphasise multiple emphasised word in a single line correctly"""
		for test, result in tests:
			self.assertEqual(MarkdownToLatex()._emphasise(test), result)
		
	def testUngreedySingleEmphasis(self):
		"""_emphasis should ensure that double asterisks are not interpreted as two single ones"""
		result = MarkdownToLatex()._emphasise("**bolded**")
		self.assertNotEqual(result, "\emph{\emph{bolded}}")
		
class Headings(unittest.TestCase):
	def testChapterHeading(self):
		tests = [("Chapter\n====", "\chapter{Chapter}"), ("Example\n=", "\chapter{Example}")]
		"""_headings should process a line of text followed by 1+ = on the next line as a chapter heading"""
		for test, result in tests:
			self.assertEqual(MarkdownToLatex()._headings(test), result)
	
	def testSectionHeading(self):
		tests = [("Section\n-----", "\section{Section}"), ("Example\n-", "\section{Example}")]
		"""_headings should process a line of text followed by 1+ - on the next line as a section heading"""
		for test, result in tests:
			self.assertEqual(MarkdownToLatex()._headings(test), result)
			
	def testSectionHeadingSpillover(self):
		"""_headings should not accidentally convert unordered list items prefixed with - into section headings"""
		test = "* Test\n- Example"
		result = MarkdownToLatex()._headings(test)
		self.assertEquals(result, test)
		
	def testAtxHeadings(self):
		tests = [("# Chapter", "\chapter{Chapter}"), ("## Section", "\section{Section}"), ("### Subsection", "\subsection{Subsection}"), ("#### Subsubsection", "\subsubsection{Subsubsection}")]
		"""_headings should process a line of text prefaced with any number of # (up to 4) and generate the appropriate heading according to this number"""
		for test, result in tests:
			self.assertEqual(MarkdownToLatex()._headings(test), result)
			
	def testAtxHeadingsTooManyHashes(self):
		"""_headings should process a line with more than 4 # as if it had only 4"""
		result = MarkdownToLatex()._headings("######### Example")
		self.assertEqual(result, "\subsubsection{Example}")
	
	def testAtxHeadingsTrailingHash(self):
		"""_headings should remove any number of trailing # from atx style headings when processing"""
		result = MarkdownToLatex()._headings("### Example ####")
		self.assertEqual(result, "\subsection{Example}")

class Lists(unittest.TestCase):
	def testUnmixedList(self):
		"""_lists should return a properly formatted list"""
		tests = [("* a\n* b\n* c", "\\begin{itemize}\n\item a\n\item b\n\item c\n\end{itemize}"), 
		("- a\n- b\n- c", "\\begin{itemize}\n\item a\n\item b\n\item c\n\end{itemize}"),
		("+ a\n+ b\n+ c", "\\begin{itemize}\n\item a\n\item b\n\item c\n\end{itemize}")]
		for test, result in tests:
			self.assertEqual(MarkdownToLatex()._lists(test), result)
			
	def testMixedUnorderedList(self):
		"""_lists should return a properly formatted list even if the prefixes are mixed"""
		tests = [("* a\n- b\n+ c", "\\begin{itemize}\n\item a\n\item b\n\item c\n\end{itemize}"), 
		("+ a\n* b\n- c", "\\begin{itemize}\n\item a\n\item b\n\item c\n\end{itemize}"),
		("- a\n+ b\n+ c", "\\begin{itemize}\n\item a\n\item b\n\item c\n\end{itemize}")]
		for test, result in tests:
			self.assertEqual(MarkdownToLatex()._lists(test), result)
			
	def testOrderedList(self):
		"""_lists should return a properly formatted ordered list"""
		tests = [('1. Beer\n2. Cars\n3. Boats', "\\begin{enumerate}\n\item Beer\n\item Cars\n\item Boats\n\end{enumerate}"),
		('2367. Beer\n12321. Cars\n5. Boats', "\\begin{enumerate}\n\item Beer\n\item Cars\n\item Boats\n\end{enumerate}"),
		('1. Beer\n1. Cars\n1. Boats', "\\begin{enumerate}\n\item Beer\n\item Cars\n\item Boats\n\end{enumerate}")]
		for test, result in tests:
			self.assertEquals(MarkdownToLatex()._lists(test), result)
		
	def testDontTouchNonLists(self):
		"""_lists should not do anything to anything that isn't a list"""
		test = "Definitely not a list."
		result = MarkdownToLatex()._lists(test)
		self.assertEquals(result, test)
		
	def testMingledLists(self):
		"""_lists should take the first item of a list as a guide to which type to use even if ordered and unordered lists are mixed together"""
		tests = [("1. Beer\n* Cars\n3. Boats", "\\begin{enumerate}\n\item Beer\n\item Cars\n\item Boats\n\end{enumerate}"),
		("* Beer\n* Cars\n3. Boats", "\\begin{itemize}\n\item Beer\n\item Cars\n\item Boats\n\end{itemize}")]
		for test, result in tests:
			self.assertEquals(MarkdownToLatex()._lists(test), result)

class Footnotes(unittest.TestCase):
	def testFootnote(self):
		"""_footnote should convert the text between ^( ... ) into footnotes"""
		result = MarkdownToLatex()._footnotes("^(A test footnote)")
		self.assertEquals(result, "\\footnote{A test footnote}")
		
	def testFootnotePassthrough(self):
		"""_footnote should leave strings without footnotes in them as is"""
		test = "Footnote-less text"
		result = MarkdownToLatex()._footnotes(test)
		self.assertEquals(result, test)

class References(unittest.TestCase):
	def testSubstituteBibliographyEntry(self):
		"""_references should process the bibliography entry correctly and remove it's definition from the output"""
		result = MarkdownToLatex()._references('[smith2008]: "Smith, Jane. *An example publication: long titles are long and much more*. New York: Imaginary Publishers, 2008." "Jane Smith, *An example publication: long titles are and much more* (New York: Imaginary Publishers, 2008)" "Smith, *An example publication*"')
		self.assertEquals(result, '')
		
	def testMalformedEntry(self):
		"""_references should not process entries with less than 3 fields"""
		test = '[smith2008]: "Smith, Jane. *An example publication: long titles are long and much more*. New York: Imaginary Publishers, 2008." "Jane Smith, *An example publication: long titles are and much more* (New York: Imaginary Publishers, 2008)"'
		result = MarkdownToLatex()._references(test)
		self.assertEquals(test, result)
		
	def testReferencePassthrough(self):
		"""_references should leave string as is without references in it"""
		test = "No references here"
		result = MarkdownToLatex()._references(test)
		self.assertEquals(result, test)
		
	def testRepeatedKey(self):
		"""_references should raise an exception if a key is used more than once"""
		tests = ['[smith2008]: "Smith, Jane. *An example publication: long titles are long and much more*. New York: Imaginary Publishers, 2008." "Jane Smith, *An example publication: long titles are and much more* (New York: Imaginary Publishers, 2008)" "Smith, *An example publication*"\n[smith2008]: "Smith, Jane. *An example publication: long titles are long and much more*. New York: Imaginary Publishers, 2008." "Jane Smith, *An example publication: long titles are and much more* (New York: Imaginary Publishers, 2008)" "Smith, *An example publication*"']
		for test in tests:
			self.assertRaises(KeyError, MarkdownToLatex()._references, test)
	
	def testURLReference(self):
		"""_references should parse URL references correctly and remove their definiton from the output"""
		tests = ('[google]: <www.google.com> "Google"', '[test]: /test "Test"')
		for test in tests:
			self.assertEquals(MarkdownToLatex()._references(test), "")
			
	def testInlineImage(self):
		"""_references should replace inline image references correctly"""
		tests = [('![test](/path/test.jpg)', '\\begin{figure}\n\includegraphics{/path/test.jpg}\n\end{figure}'), ('![test_b](/path/to/other/test.jpg "Title")', '\\begin{figure}\n\includegraphics{/path/to/other/test.jpg}\n\caption{Title}\n\end{figure}')]
		for test, result in tests:
			self.assertEquals(MarkdownToLatex()._references(test), result)
			
	def testInlineURL(self):
		"""_references should replace inline urls correctly"""
		tests = [('[an example](http://example.com "Title")', '\href{http://example.com}{an example}'), ('[This link](http://example.net/)', '\href{http://example.net/}{This link}')]
		for test, result in tests:
			self.assertEquals(MarkdownToLatex()._references(test), result)
			
	def testReferencedURL(self):
		"""_references should replace references correctly regardless of where the definition is in a relation to it for images and hyperlinks"""
		tests = [('Visit [google][] to search more.\n[google]: <www.google.com> "Google"', 'Visit \href{www.google.com}{Google} to search more.\n'), ('[test]: test.net "test"\nVisit the [test][] site.', '\nVisit the \href{test.net}{test} site.'), ('![test][]\n[test]: /test/image "Test"', '\\begin{figure}\n\includegraphics{/test/image}\n\caption{Test}\n\end{figure}\n'), ('[test]: /test/image "Test"\n![test][]', '\n\\begin{figure}\n\includegraphics{/test/image}\n\caption{Test}\n\end{figure}')]
		for test, result in tests:
			self.assertEquals(MarkdownToLatex()._references(test), result)
	
	def testUnknownKey(self):
		"""_references should raise a KeyError if an undefined reference is used"""
		tests = ["Visit [google][] for more.", "See ![test][] for more.", "Read ^[bib][] for more."]
		for test in tests:
			self.assertRaises(KeyError, MarkdownToLatex()._references, test)
			
	def testSequentialBibReferences(self):
		"""_references should generate the long form for the first time a bibliography key is referenced, short form thereafter"""
		tests = [('Read ^[smith][].\nThen read ^[smith][] again.\nThen ^[smith][] some more.\n[smith]: "Smith, Jane. *Long titles*, Somewhere: i Press, 2016." "Jane Smith, *Long titles* (Somewhere: i Press, 2016)" "Smith, *Long titles*"', 'Read Jane Smith, *Long titles* (Somewhere: i Press, 2016).\nThen read Smith, *Long titles* again.\nThen Smith, *Long titles* some more.\n')]
		for test, result in tests:
			self.assertEquals(MarkdownToLatex()._references(test), result)
			
	def testKeyedBibReferences(self):
		"""_references should replace a bibliographical reference with the requested key if one is supplied"""
		test = ('Read ^[smith][short].\nThen read ^[smith][long] again.\nThen check ^[smith][bib]\n[smith]: "Smith, Jane. *Long titles*, Somewhere: i Press, 2016." "Jane Smith, *Long titles* (Somewhere: i Press, 2016)" "Smith, *Long titles*"', 'Read Smith, *Long titles*.\nThen read Jane Smith, *Long titles* (Somewhere: i Press, 2016) again.\nThen check Smith, Jane. *Long titles*, Somewhere: i Press, 2016.\n')
		self.assertEquals(MarkdownToLatex()._references(test[0]), test[1])
		
	def testErroneousKeyedBibReferences(self):
		"""_references should raise an error if the key for a bibliographical reference from is not either long, short, or bib"""
		test = 'Read ^[smith][wrong].\n[smith]: "Smith, Jane. *Long titles*, Somewhere: i Press, 2016." "Jane Smith, *Long titles* (Somewhere: i Press, 2016)" "Smith, *Long titles*"'
		self.assertRaises(KeyError, MarkdownToLatex()._references, test)
		
if __name__ == "__main__":
	unittest.main()