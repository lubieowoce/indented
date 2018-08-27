
def binary(low, high, depth=0, prev_low=None, prev_high=None):
    assert (
        (low, high) != (prev_low, prev_high)
        if (prev_low, prev_high) != (None, None)
        else True), \
        'stuck at {}'.format((prev_low, prev_high))

    indent = '    '*depth
    if low == high-1: 
        # print(indent, '| _ ==', low, '.', sep='')
        print(indent, 'x == ', low, sep='')
    else:
        print(indent, '# [', low, ' ', high, ')', sep='')
        # mid = int(math.ceil((low + high) / 2))
        mid = ((low + high) // 2)
        # print(indent, '| _ <= ', mid, sep='')
        # print(indent, '/', '  ', low, sep='')
        print(indent, 'if x < ', mid, ':', sep='')
        binary(low, mid,  depth=depth+1, prev_low=low, prev_high=high)
        # print(indent, '\\','  ', high, sep='')
        print(indent, 'else:', sep='')
        binary(mid, high, depth=depth+1, prev_low=low, prev_high=high)


# binary(0, 4)
from indented.text import flatten_tree
from indented.codegen import if_, else_, cond, when, lit, tuple_, eval_def
from dis import dis as disassemble
import dis

def eval_tree(t, verbose=False, dis=False):
    src = flatten_tree(t)
    if verbose: print(src, end='\n\n')
    fn = eval_def(src)
    if dis:
        print(fn.__name__+':', end='\n\n')
        disassemble(fn)
        print('\n\n')
    return fn



def switch_binsearch(low, high, var, cases, prev_low=None, prev_high=None):
    assert (
        (low, high) != (prev_low, prev_high)
        if (prev_low, prev_high) != (None, None)
        else True), \
        'stuck at {}'.format((prev_low, prev_high))

    if low == high-1: 
        # print(indent, '| _ ==', low, '.', sep='')
        # var == low
        return [
            '# {} == {}'.format(var, low)] + cases[low]
    else:
        # mid = int(math.ceil((low + high) / 2))
        mid = ((low + high) // 2)
        # print(indent, '| _ <= ', mid, sep='')
        # print(indent, '/', '  ', low, sep='')
        return [
            '# {} <= {} < {}'.format(low, var, high),
            if_(var+' < '+lit(mid)),
            switch_binsearch(low, mid, var=var, cases=cases, prev_low=low, prev_high=high),
            'else:',
            switch_binsearch(mid, high, var=var, cases=cases, prev_low=low, prev_high=high),
            
        ]



def switch_linear(low, high, var, cases):
    return \
        cond([
            when(var+' == '+lit(x), cases[x])
             for x in range(low, high)
        ])

# variants = ('Foo', 'Bar', 'Zip', 'Hop', 'Woo')
variants = [chr(x) for x in range(ord('A'), ord('F')+1)]

n = len(variants)
cases = [['return "%s"' % variants[i]] for i in range(n)]

mk_def_get_variant = lambda n, switch: [
    'def get_variant(_variant_id):', [
        *switch(0, n, var='_variant_id', cases=cases)
    ]
]

get_variants = get_variant_binsearch, get_variant_linear = [
    eval_tree(mk_def_get_variant(n, switch), verbose=True, dis=True)
    for switch in (switch_binsearch, switch_linear)
]


print(dis.findlabels(get_variant_linear.__code__.co_code))
print()

get_variant_index = eval_tree([
    'def get_variant_index(_variant_id):', [
        'return '+tuple_(map(lit, variants))+'[_variant_id]'
    ]
], verbose=True, dis=True)


if __name__ == '__main__':
    import timeit
    setup_linear = "from __main__ import get_variant_linear    as get_variant"
    setup_binary = "from __main__ import get_variant_binsearch as get_variant"
    setup_index  = "from __main__ import get_variant_index     as get_variant"

    test_range = '\n'.join("get_variant(%d)" % i for i in range(n))

    tests = [
        ('test_range_linear', test_range, setup_linear),
        ('test_range_binary', test_range, setup_binary),
        ('test_range_index', test_range, setup_index ),
    ]


    n_timing_repetitions = 100001

    print("Profiling")
    for (name, code, setup) in tests:
        time_usec = timeit.timeit(
            code,
            setup=setup,
            number=n_timing_repetitions
        ) * 1000000 / n_timing_repetitions
        print('\t{name}:\t{time_usec:.2f} usec'.format(**locals()))


# choose = eval_def(choose_)
# print('choose(_variant_id):', end='\n\n')
# dis(choose)


