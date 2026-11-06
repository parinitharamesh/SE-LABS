import pytest

from cloud_storage_tier import (
    process_storage_tenants,
    monitor_replication_latency
)


# 1. Invalid input tests

def test_invalid_tenants_input():
    with pytest.raises(ValueError):
        process_storage_tenants("invalid", 10.0)


def test_negative_support_fee():
    with pytest.raises(ValueError):
        process_storage_tenants([], -5.0)


# 2. Storage tier tests

def test_hot_tier():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100, "egress_gb": 50}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 2.5, "status": "BILLED"}


def test_cool_tier_large_bucket():
    tenants = [{
        "account_active": True,
        "tier": "cool",
        "buckets": [{"size_gb": 600, "egress_gb": 0}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 8.1


def test_archive_tier():
    tenants = [{
        "account_active": True,
        "tier": "archive",
        "buckets": [{"size_gb": 100, "egress_gb": 0}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 0.5


def test_invalid_storage_tier():
    tenants = [{
        "account_active": True,
        "tier": "unknown",
        "buckets": [{"size_gb": 100}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["status"] == "ZERO_USAGE"


# 3. Tenant and bucket tests

def test_inactive_tenant():
    tenants = [{
        "account_active": False,
        "tier": "hot",
        "buckets": [{"size_gb": 100}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["status"] == "ZERO_USAGE"


def test_default_tenant_values():
    result = process_storage_tenants([{}], 10.0)
    assert result["status"] == "ZERO_USAGE"


def test_empty_tenants():
    result = process_storage_tenants([], 10.0)
    assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_invalid_bucket_size():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 0}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["status"] == "ZERO_USAGE"


def test_corrupted_hot_bucket():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100, "corrupted": True}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["status"] == "ZERO_USAGE"


def test_corrupted_archive_bucket():
    tenants = [{
        "account_active": True,
        "tier": "archive",
        "buckets": [
            {"size_gb": 100, "corrupted": True},
            {"size_gb": 200, "corrupted": False}
        ]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["status"] == "ZERO_USAGE"


# 4. Network egress and backup tests

def test_high_egress():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100, "egress_gb": 150}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 6.5


def test_backup_vault_fee():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "has_backup_vault": True,
        "buckets": [{"size_gb": 100}]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["total_billed"] == 12.5


# 5. Audit flag tests

def test_more_than_four_flagged_buckets():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "buckets": [
            {"size_gb": 0},
            {"size_gb": -1},
            {"size_gb": 0},
            {"size_gb": -5},
            {"size_gb": 0}
        ]
    }]
    result = process_storage_tenants(tenants, 10.0)
    assert result["status"] == "AUDIT_FLAGGED"


# 6. Replication latency tests

def test_no_replication_data():
    assert monitor_replication_latency([]) == "NO_DATA"


def test_replication_synced():
    assert monitor_replication_latency([[100, 150, 180]]) == "SYNCED"


def test_single_latency_spike():
    assert monitor_replication_latency([[250, 100, 250]]) == "SYNCED"


def test_consecutive_latency_spikes():
    assert monitor_replication_latency([[250, 250]]) == "SYNC_LAG_ALERT"