# import pytest

# _BREF_SKIP_REASON = (
#     "Temporarily skipped in hotfix: Baseball Reference endpoints are disabled "
#     "due to upstream Cloudflare anti-bot protections."
# )


# def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
#     """Skip BREF-dependent tests during temporary upstream outage."""
#     skip_bref = pytest.mark.skip(reason=_BREF_SKIP_REASON)

#     for item in items:
#         nodeid = item.nodeid
#         if (
#             "_bref_test.py" in nodeid
#             or "test_smoke_bref_schedule_endpoint_contract" in nodeid
#         ):
#             item.add_marker(skip_bref)
