#!/usr/bin/env python3

"""
Communicating Sequential Processes (CSP)
"""

def nil(m): return m == []
def car(m): return m[0]
def cdr(m): return m[1:]
def cons(h,t): return [h] + t

class Boom(Exception):
    # Hoare had broken machines returning 'BLEEP'
    pass

def sandbox(f, *a):
    try:
        return (True, f(*a))
    except Boom:
        return False

def STOP(event):
    """STOP is a broken machine. If we try to engage it, it will go
    'Boom!'"""
    raise Boom()

def simple(event):
    """Accept a single coin and then breakdown."""
    if event == 'coin':
        return STOP
    else:
        raise Boom()

assert sandbox(simple, 'coin')
assert not sandbox(simple, 'slug')

def prefix(c, P):
    """'Simple' is a manually constructed machine. We can use higher
    order functions to manufacture machines."""
    def machine(event):
        if event == c:
            return P
        else:
            raise Boom()
    return machine

simple2 = prefix('coin', STOP) # same as simple

def choice2(c, P, d, Q):
    def machine(event):
        if event == c:
            return P
        elif event == d:
            return Q
        else:
            raise Boom()
    return machine

c = choice2('coin', STOP, 'card', STOP)
assert c('coin') == STOP
assert c('card') == STOP

def choice3(c, P, d, Q, e, R):
    def machine(event):
        if event == c:
            return P
        elif event == d:
            return Q
        elif event == e:
            return R
        else:
            raise Boom()
    return machine

def take_only(event):
    """A machine take will take any number of coins, and do nothing
    else."""
    if event == 'coin':
        return take_only
    else:
        raise Boom()

assert take_only == take_only('coin') == take_only('coin')('coin')

def RUN(event):
    """A runaway process."""
    return RUN
assert RUN == RUN('a') == RUN('b') == RUN('a')('c')

def vms(x):
    # Version 1: explict construction
    def vms1(y):
        if y == 'choc':
            return vms
        else:
            raise Boom()
    if x == 'coin':
        return vms1
    else:
        raise Boom()
assert vms == vms('coin')('choc')('coin')('choc')

del vms
def vms(x):
    # Version 2: substitute prefix application for vms1.
    if x == 'coin':
        return prefix('choc', vms)
    else:
        raise Boom()
assert vms == vms('coin')('choc')('coin')('choc')

del vms
def vms(x):
    # Version 3.
    return prefix('coin', prefix('choc', vms))(x)

assert vms == vms('coin')('choc')('coin')('choc')

def is_trace(M, events):
    past = []
    try:
        for e in events:
            M = M(e)
            past.append(e)
    except Boom:
        # print (past,e)
        return False
    else:
        return True

def grcust(x):
    return choice3(
        'toffee', grcust,
        'choc', grcust,
        'coin', prefix('choc', grcust)) (x)

assert grcust('toffee') == grcust
assert grcust('choc') == grcust
assert grcust('coin')('choc') == grcust

def vmct(x):
    return prefix('coin', choice2('choc', vmct, 'toffee', vmct))(x)

assert vmct('coin')('choc') == vmct
assert vmct('coin')('toffee') == vmct

def intersect(P, Q):
    return lambda z: intersect(P(z), Q(z))

assert intersect(grcust, vmct)('coin')('choc')
assert intersect(grcust, vmct)('coin')('choc')('coin')('choc')
# ? assert not sandbox(intersect(grcust, vmct)('toffee'))
# intersect(grcust, vmct)('coin')('toffee')

def concurrent(P, A, Q, B):
    def f(x):
        if x in A and x in B:
            return concurrent(P(x), A, Q(x), B)
        elif x in A:
            return concurrent(P(x), A, Q, B)
        elif x in B:
            return concurrent(P, A, Q(x), B)
        else:
            raise Boom()
    return f

A = ['coin','choc','toffee']
concurrent(grcust, A, vmct, A)('coin')('choc')

noisyvm_a = ['coin','clink','choc','clunk']
def noisyvm(x):
    return prefix('coin',
                  prefix('clink', 
                         prefix('choc', 
                                prefix('clunk', noisyvm)))) (x)

cust_a = ['coin','toffee','curse','choc'] 
def cust(x):
    return prefix('coin',
                  choice2('toffee', cust,
                          'curse', prefix('choc', cust))) (x)

nc = concurrent(noisyvm, noisyvm_a, cust, cust_a)
assert is_trace(nc, ['coin','clink','curse','choc','clunk','coin'])
assert is_trace(nc, ['coin','curse','clink','choc','clunk','coin'])
assert not is_trace(nc, ['coin','clink','choc','clunk'])
assert not is_trace(nc, ['coin','clink','toffee','coin'])

def menu(a, P):
    """Discover the alphabet of P by trial."""
    if nil(a):
        return []
    else:
        try:
            P(car(a))
        except Boom:
            return menu(cdr(a), P)
        else:
            return cons(car(a),menu(cdr(a), P))

assert menu(['choc', 'a', 'b', 'coin', 'c'], vms) == ['coin']

assert is_trace(vms, ['coin'])
assert is_trace(vms, ['coin','choc'])
assert is_trace(vms, ['coin','choc','coin','choc'])
assert not is_trace(vms, ['choc'])

def SKIP(x):
    if x == '_':
        pass
    else:
        raise Boom()

player_loop_a = ['view-q', 'view-a', 'learned', 'score-yes', 'score-no']
def player_loop(x):
    return choice2('view-q', prefix('view-a', choice2('score-yes', player_loop,
                                                      'score-no', player_loop)),
                   'learned', SKIP) (x)

assert is_trace(player_loop, ['learned'])
assert is_trace(player_loop, ['view-q', 'view-a', 'score-yes', 'learned'])
assert is_trace(player_loop, ['view-q', 'view-a', 'score-no',
                              'view-q', 'view-a', 'score-yes',
                              'learned'])

dealer_loop_a = ['show-q', 'show-a', 'learned', 'score-yes', 'score-no']
def dealer_loop(x):
    return choice2('show-q', prefix('show-a', choice2('score-yes', dealer_loop,
                                                      'score-no', dealer_loop)),
                   'learned', SKIP) (x)

assert is_trace(dealer_loop, ['learned'])
assert is_trace(dealer_loop, ['show-q', 'show-a', 'score-yes', 'learned'])
assert is_trace(dealer_loop, ['show-q', 'show-a', 'score-no',
                              'show-q', 'show-a', 'score-yes',
                              'learned'])

screen_loop_a = ['open-screen', 'start', 'show-q', 'view-q', 
                 'show-a', 'view-a', 'learned', 'close-screen']

def screen_loop(x):
    return choice3('show-q', prefix('view-q', screen_loop),
                   'show-a', prefix('view-a', screen_loop),
                   'close-screen', prefix('learned', SKIP)
    ) (x)

assert is_trace(screen_loop, ['close-screen', 'learned'])
assert is_trace(screen_loop, ['show-q','view-q','close-screen', 'learned'])
assert is_trace(screen_loop, ['show-a','view-a','close-screen', 'learned'])
