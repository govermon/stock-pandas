import pytest

from stock_pandas.directive import Directive

def run_case(case, apply=False):
    c, cc, sc, a, o, e, s = case
    print('directive:', c)

    directive = Directive.from_string(c, True)

    if apply:
        directive.apply_presets()

    command = directive.command
    operator = directive.operator
    value = directive.expression

    assert command.name == cc
    assert command.sub == sc
    assert command.args == a

    if o is None:
        assert operator == o
    else:
        assert operator.name == o

    assert e == value
    assert s == str(directive)

def test_valid_columns():
    CASES = [
        (
            # directive
            'ma',
            # command name
            'ma',
            # sub command
            None,
            # arguments
            [],
            # operator
            None,
            # expression
            None,
            # to string
            'ma'
        ),
        (
            'ma.bar',
            'ma',
            'bar',
            [],
            None,
            None,
            'ma.bar'
        ),
        (
            'ma.bar:1',
            'ma',
            'bar',
            ['1'],
            None,
            None,
            'ma.bar:1'
        ),
        (
            # redundant whitespaces
            ' ma.bar:1,2  >  0 ',
            'ma',
            'bar',
            ['1', '2'],
            # invalid operator actually
            '>',
            0,

            # 0 will convert to float
            'ma.bar:1,2>0.0'
        )
    ]

    print()

    for case in CASES:
        run_case(case)

def test_valid_columns_after_apply():
    CASES = [
        (
            # directive
            'macd.dif',
            # command name
            'macd',
            # sub command
            None,
            # arguments
            [26, 12],
            # operator
            None,
            # expression
            None,
            # to string
            'macd:26,12'
        ),
        (
            'macd.signal',
            'macd',
            'signal',
            [26, 12, 9],
            None,
            None,
            'macd.signal:26,12,9'
        )
    ]

    print()

    for case in CASES:
        run_case(case, True)

def test_column_with_two_command():
    column = Directive.from_string('ma.bar: 1, 2 ,3 / boll.qux :1 ,2,3', True)
    c = column.command
    o = column.operator
    cc = column.expression

    assert c.name == 'ma'
    assert c.sub == 'bar'
    assert c.args == ['1', '2', '3']
    assert o.name == '/'
    assert cc.name == 'boll'
    assert cc.sub == 'qux'
    assert cc.args == ['1', '2', '3']
    assert str(column) == 'ma.bar:1,2,3/boll.qux:1,2,3'

def test_invalid_columns():
    with pytest.raises(ValueError, match='invalid directive'):
        Directive.from_string('a >', True)

    with pytest.raises(ValueError, match='invalid directive'):
        Directive.from_string('>', True)

    with pytest.raises(ValueError, match='invalid command'):
        Directive.from_string('a1', True)

    with pytest.raises(ValueError, match='unknown command'):
        Directive.from_string('foo', True)

    with pytest.raises(ValueError, match='invalid operator'):
        Directive.from_string('ma >> 1', True)

    with pytest.raises(ValueError, match='accepts max'):
        directive = Directive.from_string('ma:1,close,3', True)
        directive.apply_presets()

    with pytest.raises(ValueError, match='is required'):
        directive = Directive.from_string('ma', True)
        directive.apply_presets()

    with pytest.raises(ValueError, match='no sub'):
        directive = Directive.from_string('ma.nosub', True)
        directive.apply_presets()

    with pytest.raises(ValueError, match='unknown sub'):
        directive = Directive.from_string('macd.unknown', True)
        directive.apply_presets()
