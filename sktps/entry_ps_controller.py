#!/usr/bin/env python

from ps import ParameterServerController
from ps.calculator_one import CalculatorOne
from ps.calculator_many import CalculatorMany
from util.config import config


def run():
    calculators = {
        'one': CalculatorOne(),
        'many': CalculatorMany(),
    }
    t = config['ps_controller_type']
    calculator = calculators[t]
    ParameterServerController(calculator).run()


if __name__ == '__main__':
    run()
