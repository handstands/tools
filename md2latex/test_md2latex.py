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
	
if __name__ == "__main__":
	unittest.main()