"""
Basic tools for generating text with significant whitespace.

This module provides functions for creating text with significant whitespace, and indents in particular.
It defines a 'format' for describing nested, indented blocks of text not unlike Python source code.
I call it a format because it's not a class, just lists of certain shape.
This makes it easy to create a text as a python literal and work with it with minimal friction.

A text that looks like this:

aaaa
	bbbb
	cccc
		dddd
	eeee

Is represented like this:

	`['aaaa', ['bbbb', 'cccc', ['dddd'], 'eeee']]`

Or, with some room to breathe:

	[

	 'aaaa',
	 [
	     'bbbb',
	     'cccc',
	     [
	         'dddd',
	     ],
	     'eeee',
	 ],

	]

(Basically, a rose-tree of strings, except the top node must be a list.
 Or equivalently, a list of rose-trees of strings.
 If that explains it, feel free to skip the next paragraph.)


To put it in words:
	- A `text` is a list of `line`s and/or `indented blocks`.
	- A `line` is a string. (usually without leading whitespace, although there's nothing stopping you from adding some)
	- An `indented block` is a list of `line`s and/or more `indented blocks` - so, a `text`.

As a `typing` type it's

	Text = List[ Union[String, Text] ]

"""




import itertools

# TODO: Consider supporting multi-line strings of code


Node = 'Union[str, List[Node]]'
node_is_line  = lambda n: type(n) is str
node_is_block = lambda n: type(n) is list
is_node = lambda x: node_is_line(x) or node_is_block(x)

Tree = 'List[Node]'



def flatten_tree(tree: Tree) -> str:
	# return lines_to_source(tree_to_lines_rec(tree))
	return join_lines(iter_indented_lines(tree))
		
flatten = flatten_tree


def indented_lines(tree: Tree, *args, **kwargs) -> 'List[str]':
	"See `iter_indented_lines` for accurate parameters description`"
	return list(iter_indented_lines(tree, *args, **kwargs))



def join_lines(lines: 'Iterable[str]') -> str:
	return str.join("\n", lines)

join = join_lines


def iter_indented_lines(tree: Tree, indent_level_offset: int = 0, indent_string: str = "\t") -> 'Iterator[str]':
	return (indent_string*indent_level+line for (indent_level, line) in iter_lines_with_indent_level(tree))




def iter_lines_with_indent_level(tree: Tree, indent_level_offset: int = 0) -> 'Iterator[Tuple[int, str]]':
	"""
	Returns an iterator which yields succesive lines and their indent levels
	as tuples `(indent_level: int, line: str)`.
	Intuitively, `indent_level` is how many times you'd press the Tab key
	to indent a line:

	0   1   2  (indent_level)
	|   |   |   
	aaaa
		bbbb
		cccc
			dddd
		eeee


	Usage example:

	>>> tree = [
	... 
	...  'aaaa',
	...  [
	...      'bbbb',
	...      'cccc',
	...      [
	...          'dddd',
	...      ],
	...      'eeee',
	...  ],
	... 
	... ]
	>>> 
	>>> 
	>>> for x in iter_lines_with_indent_level(tree):
	...     print(x)
	...
	(0, 'aaaa')
	(1, 'bbbb')
	(1, 'cccc')
	(2, 'dddd')
	(1, 'eeee')

	"""
	# (it's way cleaner in the recursive version, as you'd expect from a function on trees)  

	indent_level = indent_level_offset

	# the stack will contain either Nodes or block markers which signify that a block begun or ended (defined below)
	stack = [] 
	stack.extend(reversed(tree)) # earlier nodes go closer to the left - the top of the stack
	# Alternatively, we could have two stacks - one for nodes and one for indents.
	# In that case when encountering a block, we'd push as many (indent_level+1)'s

	# The markers are created here, so they can't ever be in the input list.
	# Thanks to that, when we're consuming the stack we can always distinguish
	# a node from a marker using object identity (`a is b`).
	BLOCK_START = object()
	BLOCK_END   = object()
	# is_block_marker = lambda x: x is BLOCK_START or x is BLOCK_END

	while stack:
		node_or_block_marker = stack.pop()

		if node_or_block_marker is BLOCK_START:
			indent_level += 1

		elif node_or_block_marker is BLOCK_END:
			indent_level -= 1

		elif is_node(node_or_block_marker):
			node = node_or_block_marker
			if node_is_line(node):
				line = node
				yield (indent_level, line)

			elif node_is_block(node):
				nodes = node
				stack.append(BLOCK_END)
				stack.extend(reversed(nodes)) # earlier nodes go closer to the left - the top of the stack
				stack.append(BLOCK_START)

			else: raise TypeError('Expected Node, got {!r}: {!r}'.format(type(node).__qualname__, node))

		else:
			unknown = node_or_block_marker
			raise TypeError('Unexpected value of type {!r}: {!r}'.format(type(unknown).__qualname__, unknown))




# Recursive version of the above - less efficient, but way easier to verify

def indented_lines_rec(tree: Tree, indent_level: int = 0, indent_string: str = "\t") -> 'List[str]':
	return \
		concat_lists(
			_node_to_lines(node, indent_level=indent_level, indent_string=indent_string)
			for node in tree
		)
	

def _node_to_lines(node: Node, indent_level: int, indent_string: str) -> 'List[str]':
	if node_is_line(node):
		line = node
		# print('node_to_lines :: line  | indent_level =', indent_level, ',', repr(line))
		indent = indent_string * indent_level
		return [indent + line]
	elif node_is_block(node):
		# print('node_to_lines :: block | indent_level =', indent_level, ', block =')
		# pprint(node, indent=4)
		nodes = node
		return concat_lists(_node_to_lines(child, indent_level=indent_level+1, indent_string=indent_string) for child in nodes)
	else: raise TypeError('Expected Node, got {!r}: {!r}'.format(type(node).__qualname__, node))





def concat_lists(lists: 'Iterable[list]') -> list:
	return list(itertools.chain(*lists))
