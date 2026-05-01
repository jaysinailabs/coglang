# CogLang vocabulary and type definitions (CogLang Specification v1.0.2 §2.3, §2.4)
from enum import Enum

# All legal CogLang Head symbols (static vocabulary).
# COMPOSE-registered operations can dynamically extend this at runtime.
COGLANG_VOCAB: frozenset[str] = frozenset({
    # === Atomic Primitives (9) ===
    "Traverse", "Unify", "Create", "Update", "Delete",
    "Abstract", "If", "Send", "Inspect",

    # === Built-in Operations (executor native support) ===
    "Match",        # Unify alias
    "Query",        # Graph-level search [Special Form]
    "AllNodes",     # All confidence>0 node IDs
    "ForEach",      # Iteration [Special Form]
    "Do",           # Sequential execution [Special Form]
    "IfFound",      # Null/error handling [Special Form]
    "Equal",        # Structural equality
    "Compare",      # Structural diff
    "Get",          # Value extraction (dict/List/node attr)
    "Compose",      # Define compound operation [Special Form]
    "Trace",        # Execution tracing [Special Form]
    "Assert",       # Assertion check [Special Form]
    "Explain",      # Execution plan preview (stub, Phase 2)

    # === Reserved preset shortcuts ===
    "Instantiate", "Probe", "Explore",
    "Estimate", "Decompose", "Defer", "Resume", "Merge",

    # === Data Structures ===
    "List",

    # === Type Tags ===
    "Entity", "Relation", "Attribute", "Operation",
    "Rule", "LogicRule", "SelfRef",

    # === State and Boolean ===
    "True", "False",
    "NotFound",     # Query no result / target absent
    "Deferred",     # Deferred execution marker
    "Draft",        # Draft state
    "Published",    # Published state

    # === Error Types ===
    "TypeError",        # Argument type mismatch
    "ParseError",       # Parse failure
    "PermissionError",  # Insufficient permission
    "StubError",        # Stub operation called
    "RecursionError",   # Recursion depth exceeded
})
# Total: 49 built-in Heads


# Heads that represent callable or reserved operator surfaces. Data/value heads
# remain in COGLANG_VOCAB but are intentionally excluded from the operator
# catalog alignment contract.
COGLANG_OPERATOR_HEADS: frozenset[str] = frozenset({
    "Abstract", "AllNodes", "Assert", "Compare", "Compose",
    "Create", "Delete", "Decompose", "Defer", "Do",
    "Equal", "Estimate", "Explain", "Explore", "ForEach",
    "Get", "If", "IfFound", "Inspect", "Instantiate",
    "Match", "Merge", "Probe", "Query", "Resume",
    "Send", "Trace", "Traverse", "Unify", "Update",
})


# Operator heads whose argument positions contain opaque Prolog terms rather
# than nested CogLang program expressions. Validators must not recursively
# enforce CogLang head vocabulary inside these argument positions.
OPAQUE_ARG_HEADS: frozenset[str] = frozenset({
    "Match",
    "Unify",
})


# Error heads: used by executor for error propagation checks.
ERROR_HEADS: frozenset[str] = frozenset({
    "NotFound",
    "TypeError",
    "PermissionError",
    "ParseError",
    "StubError",
    "RecursionError",
})


class NodeType(Enum):
    """Graph node type enumeration (CogLang Specification v1.0.2 §2.4).

    Values are PascalCase strings matching CogLang type tag Heads.
    """
    ENTITY = "Entity"
    RELATION = "Relation"
    ATTRIBUTE = "Attribute"
    OPERATION = "Operation"
    RULE = "Rule"
    LOGIC_RULE = "LogicRule"
    SELF_REF = "SelfRef"
