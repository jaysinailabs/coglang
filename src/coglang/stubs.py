# CogLang reserved-operation stubs.
# Reserved operations return StubError[op_name, ...] until implemented.
from .parser import CogLangExpr


def _stub(op_name: str, *args) -> CogLangExpr:
    """Return StubError[op_name, *args] for a reserved operation."""
    return CogLangExpr("StubError", (op_name,) + tuple(args))


# Atomic primitives reserved for later implementation.
def send(*args):    return _stub("Send", *args)
def inspect(*args): return _stub("Inspect", *args)

# Preset shortcuts reserved for later implementation.
def abstract(*args):    return _stub("Abstract", *args)
def instantiate(*args): return _stub("Instantiate", *args)  # Phase 2+
def probe(*args):       return _stub("Probe", *args)        # Phase 1+
def explore(*args):     return _stub("Explore", *args)      # Phase 1+
def estimate(*args):    return _stub("Estimate", *args)     # Phase 1+
def decompose(*args):   return _stub("Decompose", *args)    # Phase 1+
def defer(*args):       return _stub("Defer", *args)        # Phase 1+
def resume(*args):      return _stub("Resume", *args)       # Phase 1+
def merge(*args):       return _stub("Merge", *args)        # Phase 1+
def explain(*args):     return _stub("Explain", *args)      # Phase 2+
