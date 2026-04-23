# CogLang stub operations (P0-T1, S2c-1)
# Operations not implemented in P0-T1; each returns StubError[op_name, ...].
# Spec: plans/P0-T1 任务规格书_CogLang 规范实现.md §3.1
from .parser import CogLangExpr


def _stub(op_name: str, *args) -> CogLangExpr:
    """Return StubError[op_name, *args] — signals 'not implemented in P0-T1'."""
    return CogLangExpr("StubError", (op_name,) + tuple(args))


# Atomic primitives (P0-T1 stubs — full impl in later tasks)
def send(*args):    return _stub("Send", *args)      # P0-T4 / P1+
def inspect(*args): return _stub("Inspect", *args)  # P0-T4 / P1+

# Preset shortcuts (P0-T1 stubs)
def abstract(*args):    return _stub("Abstract", *args)     # P0-T5 / ABSTRACT
def instantiate(*args): return _stub("Instantiate", *args)  # Phase 2+
def probe(*args):       return _stub("Probe", *args)        # Phase 1+
def explore(*args):     return _stub("Explore", *args)      # Phase 1+
def estimate(*args):    return _stub("Estimate", *args)     # Phase 1+
def decompose(*args):   return _stub("Decompose", *args)    # Phase 1+
def defer(*args):       return _stub("Defer", *args)        # Phase 1+
def resume(*args):      return _stub("Resume", *args)       # Phase 1+
def merge(*args):       return _stub("Merge", *args)        # Phase 1+
def explain(*args):     return _stub("Explain", *args)      # Phase 2+
