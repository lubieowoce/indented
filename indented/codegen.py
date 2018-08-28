"""## Python code generation helpers

This module contains functions that are meant to make generating python syntax easier.
They're useful when you want to avoid gluing together parentheses, commas, etc.;
and worrying about spaces between things and punctuation.
Most of them just generate strings[1].
The nice thing about that is that you can use as little or many of these functions as you want,
and keep the rest in plain string literals.

[1] Except `cond`, which generates a indented.text.Text, because
if-elif-else constructs are indented and multiline. 

	>>> def_('foo', ['x', 'y'])
	'def foo(x, y):'

	>>> with_n_([('open("xyz.txt")', 'f'), ('foo', '(x, y)')])
	'with open("xyz.txt") as f, foo as (x, y):'

	>>> apply('foo', ['a', 'b'])
	'foo(a, b)'

	>>> item('haystack', 'i')
	'haystack[i]'

	>>> tuple_([]);  tuple_(['x']);  tuple_(['x', 'y']);
	'()'
	'(x,)'
	'(x, y)'
  
'lit'() [literal] is useful if you need to splice python values somewhere.

	>>> lit([1, 2, 3])
	'[1, 2, 3]'

A `lit` can make a big difference:

	>>> apply('foo', ['abc']);   apply('foo', [lit('abc')])
	'foo(abc)'
	"foo('abc')"


Other helpers:

	>>> attr('obj', 'content')
	'obj.content'

	>>> method('turtle', 'move_to', ['x', 'y', '0'])
	'turtle.move_to(x, y, 0)'
  
"""
from .text import Tree

import itertools
from functools import partial
from inspect import cleandoc

from typing import (
	Tuple, Union,
	Optional, List, Dict, Iterable,
)
NoneType = type(None)
# Internal utils

def params_str(args: Optional[List[str]] = None, kwargs: Union[NoneType,  List[Tuple[str, str]],  Dict[str, str] ] = None) -> str:
	if kwargs is None:
		kwargs = ()
	elif isinstance(kwargs, dict):
		kwargs = kwargs.items()

	if args is None:
		args = ()
	
	kwargs_parts = (arg+'='+val for (arg, val) in kwargs)
	return '({})'.format(str.join(', ', itertools.chain(args, kwargs_parts)))

escape_brackets_for_format = lambda s: s.translate({ord('{'): '{{', ord('}'): '}}'})

blockstmt_keyword_head = lambda keyword, head: "{keyword} {head}:".format(keyword=keyword, head=head)
blockstmt_keyword = lambda keyword: keyword + ':'


# Public functions

def_  = lambda name, args: blockstmt_keyword_head('def',  name+params_str(args))
for_  = lambda pat,  expr: blockstmt_keyword_head('for',  "{pat} in {expr}".format(pat=pat, expr=expr))
with_   = lambda expr, pat:      blockstmt_keyword_head('with', "{expr} as {pat}".format(expr=expr, pat=pat))
with_n_ = lambda expr_pat_pairs: blockstmt_keyword_head('with', ', '.join("{expr} as {pat}".format(expr=expr, pat=pat) for (expr, pat) in expr_pat_pairs))

try_    = lambda: blockstmt_keyword('try')
except_ = lambda: blockstmt_keyword('except')
except_as_ = lambda expr, pat: blockstmt_keyword_head('except', "{expr} as {pat}".format(expr=expr, pat=pat))

if_   = lambda test:       blockstmt_keyword_head('if',   test)
elif_ = lambda test:       blockstmt_keyword_head('elif', test)
else_ = lambda:            blockstmt_keyword('else')


def apply(func_name: str, args: Optional[List[str]] = None, kwargs: Union[NoneType,  List[Tuple[str, str]],  Dict[str, str] ] = None) -> str:
	assert args   is None or isinstance(args,   list)
	assert kwargs is None or isinstance(kwargs, list) or isinstance(kwargs, dict)

	return func_name + params_str(args, kwargs)

item   = lambda target, index: "{target}[{index}]".format(target=target, index=index)
attr   = lambda target, attr: target + '.' + attr
method = lambda target, method, args: attr(target, apply(method, args))

def tuple_(exprs: Iterable[str], parens=True) -> str:
	# It's not a simple `'({})'.format(', '.join(exprs))`
	# because that would break the single element when:
	#   `tuple_(['a']) == '(a,)'` not `'(a)'` 
	# And this way it looks better than `'({},)'.format(', '.join(exprs))`
	parens_fmt = '({})' if parens else '{}'
	exprs = iter(exprs)
	try:
		first = next(iter(exprs))
	except StopIteration:
		return '()'
	else:
		rest_with_commas = str.join(', ', exprs)
		if rest_with_commas:
			return parens_fmt.format('{}, {}'.format(first, rest_with_commas))
		else:
			return parens_fmt.format('{},'.format(first))

dict_ = lambda pairs: '{' + str.join(', ', ('{}: {}'.format(key, val) for (key, val) in pairs) )+ '}'

escaped_literal = lambda x: escape_brackets_for_format(repr(x))
esc_lit = escaped_literal

literal = lambda x: repr(x)
lit = literal

doc = lambda s: cleandoc(s).split('\n')


default_if_blank = lambda expr, default: expr if expr else default
join = lambda *strs, sep='': str.join(sep, strs)
join_with_op = lambda exprs, op, zero: default_if_blank(str.join(' '+op+' ', ('({})'.format(expr) for expr in exprs)), default=zero)

# TODO: add util to embed double-bracketed format strings like "{{x}}" - `lit` will butcher them
# Maybe a regex replace "(\{+)" -> "$1\{",   "(\}+)" -> "$1\}" ?
# It'd be inefficient to do on every line, but can work for format strings



##########################
# Higher level functions #
##########################

def cond(cases_and_bodies: 'List[Tuple[str, Tree]]', default: 'Optional[Tree]' = None, allow_zero_cases: bool = False) -> Tree:
	"""
	Usage (note the splat):
	[
		'do_stuff()',
		*cond(
			...
		),
		'do_other_stuff()',
	]

	`allow_zero_cases`
	If this option is enabled and no conditionals are given, it simply returns the
	`else` body without an indent.
	This behavior is opt-in because a cond without any tests is usually
	a bug in code generation and should produce a loud error.
	"""
	assert isinstance(cases_and_bodies, list)

	if cases_and_bodies:
		tree = []
		(test, body), *elifs_and_bodies = cases_and_bodies
		tree.append(if_(test))
		tree.append(body)

		for (test, body) in elifs_and_bodies:
			tree.append(elif_(test))
			tree.append(body)

		if default is not None:
			tree.append(else_())
			tree.append(default)

		return tree

	elif allow_zero_cases:
		if default is not None:
			return default
		else:
			raise ValueError('cond() called without any branches')
			
	else:
		raise ValueError('`cond()` expects at least 1 if-branch.\n(pass `allow_zero_cases=True` to suppress this error and inline `else_body` instead) ')

# Readability helper for `cond` - raw tuples can look a bit messy
when = lambda test, body: (test, body) 

auto_match = partial(cond, allow_zero_cases=True)
# auto_match.__name__ = auto_match.__qualname__ = 'auto_match'



#############
# Utilities #
#############



def eval_def(src: str) -> 'Fun[..., Any]':
	""" `exec` a function definition and return the function. """  
	temp_local_namespace  = {}
	exec(src, {}, temp_local_namespace)
	assert len(temp_local_namespace) == 1, "The source:\n\n{src}\n\ndefined more than one function. locals:\n {locals}".format(src=src, locals=temp_local_namespace)
	func = next(iter(temp_local_namespace.values()))
	assert func not in globals().values(), "Function leaked into globals"
	return func





# Change the names of lambdas from '<lambda>' to however
# they're called in this module for better error messages

func = type(lambda: None)
n, v = None, None # prevent creating new variables (n, v) during loop, which messes up dict iteration
for n, v in globals().items():
	if type(v) is func and v.__name__ == '<lambda>':
		v.__name__     = n
		v.__qualname__ = n