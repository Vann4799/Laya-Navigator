from laya_navigator.preprocess.state_compactor import compact_state


def test_compact_state_keeps_stable_workflow_fields():
    result = compact_state({
        "app": "demo",
        "route": "/login",
        "page_title": "Sign in",
        "visible_elements": [{"role": "button", "name": "Sign in"}],
        "history": ["/"],
        "ignored_dom": "large html",
    })
    assert result["route"] == "/login"
    assert result["history"] == ["/"]
    assert "ignored_dom" not in result
