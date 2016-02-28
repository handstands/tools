# ATX Style Chapter title
## ATX Style Section title
### ATX Style Subsection title
#### ATX Style Subsubsection title
Also, *emphasis* and **bolding** are supported.

Regular headings like this
==========================
And this
--------
are also supported.

Unordered lists like this:
* Beer
* Cars
* Boats
are supported as well. Mixing the prefixes is perfectly possible also:
* Hair
- Feet
+ Legs
will produce the same result regardless of which prefixes are used.

Ordered lists work similarly:
1. Firstly
2. Secondly
3. Thirdly
The actual numbers are disregarded however.

Text between one asterisk or underscore will be *emphasised* _like_ *this*. Between two it will be **bolded** like __this__. Text encapsulated between two backticks will be rendered in a `monospace` font like `this`.

Unlike regular Markdown, footnotes are supported also^(this will be a footnote!). \*not emphasised\*

Inline use of images is also supported: ![test](/test/test.jpg "A Test image"). That is as long as the requisite `graphicx` package is include when rendering the outputted LaTeX. Due to the nature of it's intended output, the script disregards the Alt Text attribute. If an optional title is set, it will be processed and included as a caption. Reference-style images are supported as well. Define them somewhere in the document and include them with the usual syntax ![test_image][] and it'll work just like the other way of including them.

Similarly hyperlinks are supported. Be sure to include the `hyperref` preamble somewhere in the LaTeX header. Both inline [description](http://description.net) without and with [test](http://test.org "Testing") are supported. Again, due to the nature of LaTex versus HTML, only one of either the description and title can be shown. As only the description is required to be there, this will be used. Reference style hyperlinks are supported similarly. Visit [google][] for searching and all that jazz.

Unlike regular Markdown, this also support bibliographical references. Define them as follows:
[referenceid]: "Bibliography line here" "First citation line here" "Subsequent citations line here"

To cite them use ^[referenceid][]. By default it will replace it with the long form the first time it encounters it, and with the short form for all subsequent references. To override this use either ^[referenceid][short] for the short form, or ^[referenceid][long] for the long form. This does not affect the automatic switching between styles. Additionally, use ^[referenceid][bib] to generate the bibliography entry. Using any other key in this fashion other than those three mentioned here will result in an exception.

[smith2008]: "Smith, Jane. *An example publication: long titles are long and much more*. New York: Imaginary Publishers, 2008." "Jane Smith, *An example publication: long titles are and much more* (New York: Imaginary Publishers, 2008)" "Smith, *An example publication*"
[google]: <www.google.com> "Google"
[test_image]: /path/to/image.jpg "An example image"