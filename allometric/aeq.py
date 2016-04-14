from sympy.parsing.sympy_parser import parse_expr, standard_transformations, convert_xor
from sympy import Symbol, Wild
from django.db.models.loading import get_model


# Transformations do different things while parsing string
# 1) Standard transformations (automatically converts text to Symbols, among other things)
# 2) convert_xor converts ^ notation to exponent ** notation
# 3) My custom transformation: function_exponents_and_implicit_multiplication_only
# Here, I had to modify the packaged implicit_multiplication_application in sympy==0.7.2-git to only use steps _function_exponents and _implicit_multiplication
#from sympy.parsing.sympy_parser import _function_exponents, _implicit_multiplication, _flatten
#def function_exponents_and_implicit_multiplication_only(result, local_dict, global_dict):
#    for step in (_function_exponents,
#                 _implicit_multiplication):
#        result = step(result, local_dict, global_dict)
#    result = _flatten(result)
#    return result
# The transformations argument must have this weird tuple construction:
#transformations = (standard_transformations + (function_exponents_and_implicit_multiplication_only,))
#transformations = (transformations + (convert_xor,))

from sympy.parsing.sympy_parser import split_symbols_custom, convert_xor, _implicit_multiplication, \
implicit_multiplication, function_exponentiation, implicit_application

transformations = standard_transformations + (convert_xor, \
_implicit_multiplication, implicit_multiplication, function_exponentiation, implicit_application)

def agb2bgb(agb, root_shoot_ratio):
    return (agb * root_shoot_ratio)


def kdm2tc(kdm):
    return kdm / 1000.0 * .47


def tc2tdm(tc):
    return tc / .47


def kdm2tdm(kdm):
    return kdm / 1000.0


def is_aeq_invalid(aeq_string):
    if aeq_string is None or aeq_string == '':
        return "The string field cannot be empty"
    expression = parse_expr(aeq_string, transformations=transformations)

    symbols = expression.atoms(Symbol)
    constants = expression.atoms().difference(symbols)

    w = Wild('w', exclude=[0, 1])
    x = Wild('x', exclude=[0, 1])
    y = Wild('y', exclude=[0, 1])

    # Validation #1 - No triple exponentiation
    if expression in expression.find(w**x**y):
        return "Bad expression: Triple exponentiation (w^x^y) is prohibited."

    # Validation #2 - No constants > 999 or < 1/999 (0.001001...)
    for constant in constants:
        c = abs(float(constant))
        if c > 9999999.0:
            return "Bad expression: Constant is larger than 999,999. [%s]" % expression
        elif c < (1/9999999.0):
            return "Bad expression: Constant is smaller than 1/999,999 (0.001001...). [%s]" % expression

    # Validation #3 - Symbol must exist in tree fields
    fields = get_model('mrvapi', 'Tree')._meta.get_all_field_names()
    for symbol in symbols:
        if str(symbol) not in fields:
            return "Bad expression: parameter %s is not valid (options are dbh, total_height, crown_d_max, crown_d_90, wood_gravity)." % (symbol)

    return False  # this is backwards! we want a False return, as strings are True ...


def get_agb_result(aeq_string, tree, verbose=False):

    expression = parse_expr(aeq_string, transformations=transformations)

    symbols = expression.atoms(Symbol)

    parameters = dict()
    for parameter in map(lambda x: str(x), list(symbols)):
        parameters[parameter] = getattr(tree, parameter, 1)

    result = expression.subs(parameters)

    if verbose:
        return expression, parameters, result
    else:
        return result

