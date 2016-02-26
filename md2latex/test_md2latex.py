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
		
if __name__ == "__main__":
	unittest.main()