import argparse

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/26'

def create_main_remote_group(parser_to_add_to):
    append_view_remote_group_to_main_remote(parser_to_add_to)

def append_view_remote_group_to_main_remote(remote_parser):
    view_remote_group = remote_parser.add_argument_group('view-remote-group')
    view_remote_group.add_argument('--global', help="Used to specify a global remote", action='store_true', dest='glob')
    view_remote_group.add_argument('-v', '--verify', help="Verify remote", action='store_true')
