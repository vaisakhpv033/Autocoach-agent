"""Unit tests for reporting security (SSRF prevention) and payload generation."""

import pytest
from autocoach.reporting import is_safe_webhook_url


def test_is_safe_webhook_url_valid_https():
    """Verify that legitimate public HTTPS URLs are permitted."""
    assert is_safe_webhook_url("https://translation.vaisakhpv.space/api/v1/autocoach/reports") is True
    assert is_safe_webhook_url("https://api.myclinic.com/webhook") is True


def test_is_safe_webhook_url_blocks_ssrf_metadata():
    """Verify that cloud metadata service endpoints (AWS/GCP/Azure) are strictly blocked."""
    assert is_safe_webhook_url("http://169.254.169.254/latest/meta-data/") is False
    assert is_safe_webhook_url("http://metadata.google.internal/computeMetadata/v1/") is False
    assert is_safe_webhook_url("http://metadata.azure.internal/metadata/instance") is False
    assert is_safe_webhook_url("http://instance-data/latest/meta-data") is False


def test_is_safe_webhook_url_blocks_private_networks():
    """Verify that loopback and private RFC-1918 IPs are blocked when allow_local=False."""
    assert is_safe_webhook_url("http://127.0.0.1:8000/report", allow_local=False) is False
    assert is_safe_webhook_url("http://localhost:8000/report", allow_local=False) is False
    assert is_safe_webhook_url("http://10.0.0.1/report", allow_local=False) is False
    assert is_safe_webhook_url("http://192.168.1.50/report", allow_local=False) is False
    assert is_safe_webhook_url("http://172.16.0.1/report", allow_local=False) is False


def test_is_safe_webhook_url_allows_local_when_flagged():
    """Verify that local development URLs are permitted only when allow_local=True."""
    assert is_safe_webhook_url("http://127.0.0.1:8000/report", allow_local=True) is True
    assert is_safe_webhook_url("http://localhost:8000/report", allow_local=True) is True


def test_is_safe_webhook_url_blocks_invalid_schemes():
    """Verify that non-http/https schemes are blocked."""
    assert is_safe_webhook_url("file:///etc/passwd") is False
    assert is_safe_webhook_url("gopher://127.0.0.1:70") is False
    assert is_safe_webhook_url("ftp://example.com/file") is False
    assert is_safe_webhook_url("") is False
    assert is_safe_webhook_url(None) is False

