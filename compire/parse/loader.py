
import re
from functools import reduce
from .atoms import Production, NTerm, Term, Value, Code, Null


def strip_comments(stream):
    """Strip comments, tail comments, but keep # in quotations."""
    switch = '\'"'
    quoted = False
    quotation = None
    triplet = 0
    mulline = False
    commented = False
    code = ''
    for num, i in enumerate(stream):
        if triplet:
            code += i
            triplet -= 1
            continue
        if i in switch:
            if not quoted:
                quoted = True
                quotation = i
                if stream[num+1] == stream[num+2] == i:
                    triplet = 2
                    mulline = True
            else:
                if i == quotation:
                    if mulline:
                        if stream[num+1] == stream[num+2] == i:
                            triplet = 2
                            mulline = False
                            quoted = False
                            quotation = None
                    else:
                        quoted = False
                        quotation = None
        elif i == '#':
            if not quoted:
                commented = True
        elif i == '\n' and commented and not mulline:
            commented = False
        if commented:
            code += ' '
        else:
            code += i
    return code


def separate_productions(code):
    c = re.sub(r"(?m)^(\w+)(\s*?)(:==)", r"\3\2\1", code)
    c_split = [i for i in re.split(":==", c) if i]
    return c_split


def get_none_terminals(prod_str_list):
    n_terms = []
    #spec = r"(?s)^\s*(?P<Head>\w+).*?(?P<Nullable>(?:\|\s*|\|\s*{{.*}}\s*)?$)"
    spec = re.compile(r"""(?s)^\s*?(?P<Head>\w+)     # head Nterm
                          .*?                  # any character
                          (?P<Nullable>(?:\|\s*|\|\s*{{.*}}\s*)?$)""", re.X)
    for p in prod_str_list:
        res = re.match(spec, p).groups()
        nterm = NTerm(res[0], bool(res[1]))
        if nterm not in n_terms:
            n_terms.append(nterm)
        else:
            if nterm.nullable:
                n_terms[n_terms.index(nterm)] = nterm
    return n_terms


#def get_terminals_values(grammar_code, n_terms):
#    term_values = []
#    terminals = []
#    codes = []
#    spec = [r"(?P<Produce>:==)",
#            r"(?P<Seperate>\|)",
#            r"(?P<Spaces>\s+)",
#            r"(?P<quote>[\"'])(?P<Value>\S+)(?P=quote)",
#            r"(?P<Term>\w+)",
#            r"{{(?P<Code>\w+)}}",
#            ]
#    pattern = "|".join(spec)
#    for mo in re.finditer(pattern, grammar_code):
#        kind = mo.lastgroup
#        value = mo.group(kind)
#        if kind == "Value":
#            v = Value(value)
#            if v not in term_values:
#                term_values.append(v)
#        elif kind == "Term":
#            if NTerm(value) not in n_terms:
#                v = Term(value)
#                if v not in terminals:
#                    terminals.append(v)
#        elif kind == "Code":
#            sym = "Cd" + str(len(codes))
#            v = Code(sym, value)
#            if v not in codes:
#                codes.append(v)
#        else:
#            # ignore Produce Seperate Spaces and Rule
#            pass
#    return terminals, term_values, codes


def decompose_prod(prod, n_terms, values, terms, codes):
    p = r"(?s)^\s*?(\w+)\s*(.*)$"
    h_str, units = re.match(p, prod).groups()
    head = n_terms[n_terms.index(NTerm(h_str))]
    bodies = re.split(r"\|", units)
    productions = []
    null_prods = []
    spec = [r"(?P<Spaces>\s+)",
            r"(?P<quote>[\"'])(?P<Value>\S+)(?P=quote)",
            r"(?P<Term_NTerm>\w+)",
            r"{{(?P<Code>\w+)}}",
            ]
    pattern = "|".join(spec)
    for body in bodies:
        formlist = []
        for symbol in re.finditer(pattern, body):
            kind = symbol.lastgroup
            value = symbol.group(kind)
            if kind == "Value":
                v = Value(value)
                formlist.append(v)
                if v not in values:
                    values.append(v)
            elif kind == "Term_NTerm":
                if NTerm(value) in n_terms:
                    t = n_terms[n_terms.index(NTerm(value))]
                    formlist.append(t)
                else:
                    t = Term(value)
                    formlist.append(t)
                    if t not in terms:
                        terms.append(t)
            elif kind == "Code":
                t = Code(f"CD{str(len(codes))}", value)
                formlist.append(t)
                codes.append(t)
                nullprod = Production(t, (Null(),), lambda: None)
                null_prods.append(nullprod)
        production = Production(head, tuple(formlist), lambda: None)
        productions.append(production)
    return productions, null_prods, values, terms, codes


def eliminate_null_production(grammar):
    new_gram = []
    grams = list(map(lambda p: p.remove_null(), grammar))
    for i in grammar:
        prods = i.remove_null()
        for p in prods:
            if p not in new_gram:
                new_gram.append(p)
    return new_gram


def load_grammar(grammar_file):
    """Read rules from grammar file, parse and return intermediates.

    For example::

        from compire.parse.loader import load_grammar
        gram_file = "a.grammar"      # the file with correct path needed
        grammar, symbols, env = load_grammar(gram_file)

    :param grammar_file: grammar rules in *.grammar file.
    :return: a tuple contains a grammar list, a symbols list, and an env.
    """

    grammar = []
    env = {}

    with open(grammar_file) as f:
        # 1. seperate file by  ----------------- seperate line
        raw_grammar, definitions = re.split(r"(?m)^[\s-]+[-]+[\s-]+$", f.read())

        # 2. augment syntax
        aug_grammar = 'startsup :== start "$" \n' + raw_grammar
        aug_definitions = definitions + '\n\ndef startsup(f):\n    return f()'

        # 3. get definition funcs into namespace
        exec(aug_definitions, env)

        # 4. strip comments
        pure_grammar = strip_comments(aug_grammar)

        # 5. get productions with | operators.
        prods = separate_productions(pure_grammar)

        # 6. get none terminals list
        n_terms = get_none_terminals(prods)

        # 7. get terminals and terminal values list. And all symbols list
        #terms, values, codes = get_terminals_values(pure_grammar, n_terms)

        #symbols = values + terms + n_terms + codes

        # 8. generate grammar list, contains production rules.
        values, terms, codes, null_prod_list = [], [], [], []
        for prod in prods:
            result = decompose_prod(prod, n_terms, values, terms, codes)
            p_list, n_list, values, terms, codes = result
            null_prod_list.extend(n_list)
            grammar.extend(p_list)
        grammar.extend(null_prod_list)

        symbols = [Null()] + values + terms + n_terms + codes

        # 9. eliminate null productions.
        new_grammar = eliminate_null_production(grammar)

        return new_grammar, symbols, env

