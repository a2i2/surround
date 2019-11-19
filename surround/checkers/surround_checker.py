from pylint import checkers
from pylint import interfaces
from pylint.checkers import utils

class SurroundChecker(checkers.BaseChecker):
    __implements__ = interfaces.IAstroidChecker

    name = 'surround-convention'

    msgs = {
        'C0001': (
            "Use of print instead of logging statements",
            'surround-avoid-print',
            'Used when a script uses print instead of a logging statement',
        )
    }

    @utils.check_messages('surround-avoid-print')
    def visit_call(self, node):
        if node.func.as_string() == "print":
            self.add_message('surround-avoid-print', node=node)

def register(linter):
    linter.register_checker(SurroundChecker(linter))
