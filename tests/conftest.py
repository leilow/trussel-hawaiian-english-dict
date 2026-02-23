"""Shared fixtures for CHD scraper tests."""

from pathlib import Path

import pytest

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def raw_dir():
    return RAW_DIR


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR
