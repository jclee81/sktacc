#!/usr/bin/env python

from ps import ParameterServerController
from ps.calculator_mono import CalculatorMono


def run():
    calculator = CalculatorMono()
    ParameterServerController(calculator).run()


if __name__ == '__main__':
    run()
