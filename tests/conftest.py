import pytest

def pytest_addoption(parser):

    parser.addoption("--no-qt", action="store_true",
        help="Do not run Qt tests")

def pytest_collection_modifyitems(config, items):
    noqt =  config.getoption("--no-qt")

    skip_qt   = pytest.mark.skip(reason="Qt Test explicitely excluded")

    # skip_test = pytest.mark.skip(reason="skip all for now")
    for item in items:
        if "qt" in item.keywords and noqt:
            item.add_marker(skip_qt)
