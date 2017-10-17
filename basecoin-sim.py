"""
TODO:
1. Queue cap
2. Risk-neutral bond pricing
3. Price movements with skewed distributions
"""

import random

TOTAL_SUPPLY = 10000000
UPDATE_TIME = 20 # Minutes

DRIFT = 0
VOLATILITY = 0.045

QUEUE_CAP = 5 * 365 * 24 * 60 / UPDATE_TIME # Queue cap in number of "steps"

global_state = {
    't': 0,
    'bond_queue': [],
    'coin_supply': TOTAL_SUPPLY,
    'shareholder_coins': 0
}


def compute_bond_price(state):
    return 1


def increase_supply(exchange_rate, state):
    # Number of newly minted coins
    supply_delta = int(TOTAL_SUPPLY * (exchange_rate - 1))

    state['coin_supply'] += supply_delta
    # Pay bonds
    while supply_delta > 0 and len(state['bond_queue']) > 0:
        next_bond_tuple = state['bond_queue'].pop(0)
        t, amount = next_bond_tuple
        if amount > supply_delta:
            supply_delta = 0
            state['bond_queue'].insert(0, (t, amount - supply_delta))
        else:
            supply_delta -= amount

    # Pay dividends to shareholders
    if supply_delta > 0:
        state['shareholder_coins'] = supply_delta

    return state


def decrease_supply(exchange_rate, state):
    # Number of coins to auction/burn
    supply_delta = int(TOTAL_SUPPLY * (1 - exchange_rate))
    bond_price = compute_bond_price(state)
    state['bond_queue'].append((state['t'], int(supply_delta / bond_price)))
    state['coin_supply'] -= supply_delta
    return state


def generate_new_price():
    return 1 + random.gauss(DRIFT, VOLATILITY)


def get_queue_length(bond_queue):
    return sum([x[1] for x in bond_queue])


def print_state(state):
    print 'STATE t=%d' % state['t']
    print '  Total Supply (incl. sharholder coins): %d' % state['coin_supply']
    print '  Queue elements: %s' % len(state['bond_queue'])
    print '  Queue length: %d' % get_queue_length(state['bond_queue'])
    print '  Sharedholder coins: %s' % state['shareholder_coins']


def print_price_change(price):
    if price > 1:
        print 'Upward movement by %.4f%%' % ((price - 1) * 100)
    elif price < 1:
        print 'Downward movement by %.4f%%' % ((1 - price) * 100)
    else:
        print 'Price didn\'t move'


def step(state, debug=True, check_edge_conditions=True):
    price = generate_new_price()
    if price > 1:
        state = increase_supply(price, state)
    elif price < 1:
        state = decrease_supply(price, state)

    if debug:
        print_price_change(price)
        print_state(state)
        raw_input()
    if check_edge_conditions:
        if state['coin_supply'] <= 0:
            print 'Edge condition met: supply hit 0 at t=%d' % state['t']
            return None

    state['t'] += 1
    return state


def run_simulation(max_steps):
    state = dict(global_state) # Copy
    for _ in xrange(max_steps):
        result = step(state, debug=False, check_edge_conditions=True)
        if result is None:
            return False # Edge condition met - return failure mode
    return True # No edge conditions met - pass

if __name__=='__main__':
    # Monte Carlo
    num_simulations = 250
    max_steps = 365 * 24 * 60 / UPDATE_TIME # 1 year
    num_successes = 0

    for _ in xrange(num_simulations):
        if run_simulation(max_steps):
            num_successes += 1

    print ('%% Successes in %d simulations (%d timesteps simulation 1 yr):'
           ' %.2f%%' % (num_simulations, max_steps,
                        float(num_successes) / num_simulations * 100))
