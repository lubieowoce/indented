# allow this module to import the whole package
if __name__ == '__main__':
	import pathlib
	import sys

	here = pathlib.Path(__file__).resolve()
	parent_package_location = here.parents[2]
	sys.path.append(str(parent_package_location))


def run_doctests():
	import doctest
	from indented import text
	from indented import codegen

	for mod in (text, codegen):
		failure_count, test_count = doctest.testmod(mod)
		if failure_count == 0:
			print("{mod.__name__}: ran {test_count} tests, passed everything".format(**locals()))
		else:
			print("{mod.__name__}: ran {test_count} tests, failed {failure_count}".format(**locals()))
			raise Exception('Module {mod.__name__} failed {failure_count} test(s)'.format(**locals()))
	print()



from indented.text import *
from indented.codegen import *

def demo():

	from pprint import pprint
	sep = lambda: print("\n" * 2)

	cond_ = lambda branches, default: [
	'def sign(x):', [
		'print("sign :: ", x)',
		*auto_match(
			branches,
			default,
		),
	]
	]
	cond = cond_(
		[('x > 0',  ['return "positive"']),
		 ('x == 0', ['return "zero"']),
		 ('x < 0',  ['return "negative"'])],

		['return "weird"'],
	)
	print(flatten(cond))
	sep()

	cond0 = cond_(
		[],
		['return "default"']
	)
	print(flatten(cond0))
	sep()


	print(apply('foo', ['x'], {'a': '5', 'b': '10'}))
	sep()

	# TODO: move `app, method, attr` uses to another example - they're not useful here.
	# Arguably, `attr` is pretty useless,
	# and `app, method` are only useful if the args/kwargs vary depending on compile-time values
	# Writing them literally in the string will be clearer most of the time

	t0 = [
	def_('{name}', ['{a}', '{b}']), [
		*doc('''"""
		doc...
		string
		"""'''),
		'',
		'global m',
		if_(item('{b}', lit(0))+' > 8 and '+apply('bar', ['{b}'])+' and {a} > 0'), [
			'print({a})',
			'print({a}+1)',
		],
		else_(), [
			'print({a}/2)'
		],
		for_('e', '{b}'), [
			apply('print', ['e', lit({"hey": 3}), attr('e', 'zap')]),
			apply('print', [method('e', 'dop', [lit("ghi"), lit(15)])])
		],
		'',
		'@some_decorator',
		def_('zee', []), [
			'return {b}[3] % 2'
		],
		'',
		try_(), [
			'do_stuff()',
		],
		except_as_('SomeException', 'e'), [
			apply('handle', [lit("oops")], {'cause': lit(3)}),
		],
		'',
		'return {a}',
	]
	]

	t = [
	'def {name}({a}, {b}):', [
		*doc('''"""
		doc...
		string
		"""'''),
		'',
		'global m',
		'if {b}[0] > 8 and bar({b}) and {a} > 0:', [
			'print({a})',
			'print({a}+1)',
		],
		'else:', [
			'print({a}/2)'
		],
		'for e in {b}:', [
			'print(e, {{\'hey\': 3}}, e.zap)',
			'print(e.dop(\'ghi\', 15))',
		],
		'',
		'@some_decorator',
		'def zee():', [
			'return {b}[3] % 2'
		],
		'',
		'try:', [
			'do_stuff()',
		],
		'except SomeException as e:', [
			'handle(\'oops\', cause=3)',
		],
		'',
		'return {a}',
	]
	]

	t1 = t
	if t0 != t1:
		if len(t0) != len(t1):
			raise AssertionError('differing lenghts', len(t0), len(t1))
		else:
			differing = [
				(ln_num, l0, l1)
				for (ln_num, (l0, l1)) in enumerate(zip(iter_indented_lines(t0), iter_indented_lines(t1)), 1)
				if l0 != l1
			]
			print(*differing, sep="\n")
			raise AssertionError

	li = list(iter_lines_with_indent_level(t))
	pprint(li)
	sep()

	s = flatten(t)
	print(s)
	sep()


	ss = s.format(name='foo', a='x', b='y')
	print(ss)
	sep()

	ns = {}
	exec(ss, {}, ns)
	foo = ns['foo']

	print(foo)
	help(foo)


if __name__ == '__main__':
	run_doctests()
	demo()