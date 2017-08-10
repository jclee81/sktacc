#!/usr/bin/env python
import threading
import time

from ps import ParameterServerController
from ps.calculator_many import CalculatorMany
from ps.calculator_one import CalculatorOne
from util.config import config


def loop_calculator(calculator):
    while True:
        calculator.loop()
        time.sleep(0.001)


def run():
    calculators = {
        'one': CalculatorOne(),
        'many': CalculatorMany(),
    }
    t = config['ps_controller_type']
    calculator = calculators[t]
    t1 = threading.Thread(target=loop_calculator, args=(calculator,))
    t1.daemon = True
    t1.start()
    ParameterServerController(calculator).run()


if __name__ == '__main__':
    run()
