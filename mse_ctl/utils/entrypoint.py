"""mse_ctl.utils.entrypoint module."""

import ast
from pathlib import Path

IMPORT_TEMPLATE = """
from cosmian_lib_sgx import Enclave
"""

IF_MAIN_TEMPLATE = """
if __name__ == "__main__":
    main()
"""

ENTRYPOINT_TEMPLATE = """
def main() -> int:
    with Enclave() as enclave:
        pass
    return 0
"""


def compare_ast(node1: ast.AST, node2: ast.AST) -> bool:
    """Naive comparison of AST dump."""
    if type(node1) != type(node2):  # pylint: disable=unidiomatic-typecheck
        return False

    return ast.dump(node1) == ast.dump(node2)


class NodeVisitor(ast.NodeVisitor):
    """NodeVisitor to visit a python ast tree.

    Parameters
    ----------
    has_if_main: bool
        True if the tree contains the main if statement.
    has_import: bool
        True if the tree contains the `cosmian_lib_sgx` import.
    has_entrypoint: bool
        True if the main body is wrapped inside a `with` statement.

    """

    def __init__(self):
        """Init constructor of NodeVisitor."""
        self._has_if_main = False
        self._has_import = False
        self._has_entrypoint = False
        self._entrypoint_template = ast.parse(ENTRYPOINT_TEMPLATE).body[0]
        self._if_main_template = ast.parse(IF_MAIN_TEMPLATE).body[0]
        self._import_template = ast.parse(IMPORT_TEMPLATE).body[0]

    @property
    def has_if_main(self) -> bool:
        """Say if the `run.py` has a valid main if statement."""
        return self._has_if_main

    @property
    def has_import(self) -> bool:
        """Say if the `run.py` has the expected import."""
        return self._has_import

    @property
    def has_entrypoint(self) -> bool:
        """Say if the `run.py` has a valid `main()` function."""
        return self._has_entrypoint

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Call used when node is a ImportFrom. Search for `cosmian_lib_sgx` import."""
        if self._has_import:
            return

        self._has_import = compare_ast(self._import_template, node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Call used when node is a FunctionDef. Analyse the `main()` function."""
        if self._has_entrypoint:
            return

        # Ignore the test for function name != 'main'
        if node.name == self._entrypoint_template.name:
            # Args and return type should be the same as expected
            if not compare_ast(
                    self._entrypoint_template.args,
                    node.args) or node.returns is None or not compare_ast(
                        self._entrypoint_template.returns, node.returns):
                return

            # Clean up the body to analyse fairly the body
            body_no_comment = [
                x for x in node.body if not isinstance(x, ast.Expr)
            ]

            # At this point, we should only have two statements in the functin body
            if len(body_no_comment) != 2:
                return

            # The first statement should be a `with`
            if not isinstance(body_no_comment[0], ast.With):
                return

            # Compare the parameters of the `with` but ignore its body
            if not body_no_comment[0].items or not compare_ast(
                    self._entrypoint_template.body[0].items[0],
                    body_no_comment[0].items[0]):
                return

            # The second statement should be a `return`
            if not compare_ast(self._entrypoint_template.body[1],
                               body_no_comment[1]):
                return

            self._has_entrypoint = True

    def visit_If(self, node: ast.If):
        """Call used when node is a If. Search for the main if statement."""
        if self._has_if_main:
            return

        # Compare the operands and the operator of the if
        if not compare_ast(self._if_main_template.test, node.test):
            return

        # Compare the body of the if statement
        self._has_if_main = node.body and compare_ast(
            self._if_main_template.body[0], node.body[0])


def validate_entrypoint(entrypoint_path: Path):
    """Proceed some checks on the `run.py` content and raise if it's invalid."""
    tree = ast.parse(entrypoint_path.read_text(encoding="utf-8"))

    node_visitor = NodeVisitor()
    node_visitor.visit(tree)

    if not node_visitor.has_if_main:
        raise Exception(
            "Your run.py is malformed. "
            f"The following section could not be found: {IF_MAIN_TEMPLATE}")

    if not node_visitor.has_import:
        raise Exception(
            "Your run.py is malformed. "
            f"The following section could not be found: {IMPORT_TEMPLATE}")

    if not node_visitor.has_entrypoint:
        raise Exception(
            "Your run.py is malformed. "
            f"The following section could not be found: {ENTRYPOINT_TEMPLATE}")
