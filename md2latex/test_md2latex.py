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
		
	def testUngreedySingleEmphasis(self):
		"""_emphasis should ensure that double asterisks are not interpreted as two single ones"""
		result = MarkdownToLatex()._emphasise("**bolded**")
		self.assertNotEqual(result, "\emph{\emph{bolded}}")
	
if __name__ == "__main__":
	unittest.main()