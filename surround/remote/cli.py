import argparse

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/26'

def create_main_remote_group(parser_to_add_to):
    remote_group = parser_to_add_to.add_argument_group('group')
    remote_group.add_argument('--global', help="Used to specify a global remote", action='store_true', dest='glob')
