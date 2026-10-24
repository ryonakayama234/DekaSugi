"""Protocol and bounded execution tests for EXP-0001."""
import unittest

from packages.library import DEFAULT_REGISTRY
from packages.protocol import (
    Input, Call, DSLValidationError, parse_program, program_to_dict,
    program_hash, check_program, parse_task,
)
from packages.runtime import evaluate


class ProtocolTests(unittest.TestCase):
    def test_program_round_trip(self):
        ast = Call("lower", Call("trim", Input()))
        self.assertEqual(parse_program(program_to_dict(ast)), ast)
        self.assertEqual(program_hash(ast), program_hash(parse_program(program_to_dict(ast))))

    def test_invalid_unknown_operation_rejected(self):
        with self.assertRaises(DSLValidationError):
            evaluate(Call("os.system", Input()), "hi")

    def test_type_mismatch_rejected_before_evaluation(self):
        with self.assertRaises(DSLValidationError):
            evaluate(Call("trim", Input("Integer")), "hi")
        with self.assertRaises(DSLValidationError):
            check_program(Call("trim", Input(), "Integer"), DEFAULT_REGISTRY.signatures)

    def test_bad_ast_shapes_rejected(self):
        with self.assertRaises(DSLValidationError):
            parse_program({"node_kind": "call", "type": "String", "op_id": "trim", "children": []})
        with self.assertRaises(DSLValidationError):
            parse_program({"node_kind": "input", "type": "String", "injected": 1})

    def test_node_budget(self):
        ast = Call("lower", Call("trim", Input()))
        self.assertEqual(check_program(ast, DEFAULT_REGISTRY.signatures, max_nodes=3), 3)
        with self.assertRaises(DSLValidationError):
            evaluate(ast, " X ", max_nodes=2)

    def test_exact_interpreter_semantics(self):
        ast = Call("lower", Call("trim", Input()))
        self.assertEqual(evaluate(ast, "  RED "), "red")
        self.assertEqual(evaluate(Call("upper", Input()), "hi"), "HI")
        self.assertEqual(evaluate(Input(), " hi "), " hi ")

    def test_task_limits_and_fields_validated(self):
        task = {"schema_version": "0.1", "domain": "string_to_string",
                "task_id": "t", "examples": [{"input": "a", "output": "a"}]}
        self.assertEqual(parse_task(task).task_id, "t")
        for invalid in (0, -1, True, 100001):
            with self.subTest(invalid=invalid), self.assertRaises(DSLValidationError):
                parse_task({**task, "limits": {"max_candidates": invalid}})
        with self.assertRaises(DSLValidationError):
            parse_task({**task, "examples": [{"input": 1, "output": "a"}]})

    def test_runtime_requires_string(self):
        with self.assertRaises(DSLValidationError):
            evaluate(Input(), 42)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
