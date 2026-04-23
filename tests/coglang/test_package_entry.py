from __future__ import annotations

import importlib
import sys


def test_logos_package_import_is_lightweight():
    sys.modules.pop("logos", None)
    sys.modules.pop("logos.query_net", None)
    sys.modules.pop("logos.soft_graph_memory", None)

    logos = importlib.import_module("logos")

    assert logos.__version__ == "0.1.0"
    assert "logos.query_net" not in sys.modules
    assert "logos.soft_graph_memory" not in sys.modules


def test_logos_querynet_lazy_import():
    sys.modules.pop("logos", None)
    sys.modules.pop("logos.query_net", None)

    logos = importlib.import_module("logos")
    query_net_cls = logos.QueryNet

    assert query_net_cls.__name__ == "QueryNet"
    assert "logos.query_net" in sys.modules
