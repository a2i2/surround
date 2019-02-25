import argparse

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/26'

def add_group_to_parser(parser_to_add_to):
    return parser_to_add_to.add_argument_group('group')
