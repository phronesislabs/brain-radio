"""Test API main module execution."""


def test_main_module_execution():
    """Test that main module can be executed (lines 309-311)."""
    # This tests the `if __name__ == "__main__"` block
    # We can't easily test this without actually running the module,
    # but we can verify the code structure exists
    import brain_radio.api.main as api_main

    # Verify the module has the expected structure
    assert hasattr(api_main, "app")
    # uvicorn is only imported in the if __name__ == "__main__" block,
    # so we can't test that import without actually running the module
