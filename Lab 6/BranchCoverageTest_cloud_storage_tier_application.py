import pytest

from cloud_storage_tier import (
    process_storage_tenants,
    monitor_replication_latency
)


# 1. Input validation branches

def test_invalid_tenant_type():
    with pytest.raises(ValueError):
        process_storage_tenants("invalid", 10)


def test_negative_fee():
    with pytest.raises(ValueError):
        process_storage_tenants([], -1)


def test_valid_empty_tenant_list():
    assert process_storage_tenants([], 10) == {
        "total_billed": 0.0,
        "status": "ZERO_USAGE"
    }


# 2. Account activity branches

def test_active_account():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100}]
    }], 10)
    assert result["status"] == "BILLED"


def test_inactive_account():
    result = process_storage_tenants([{
        "account_active": False,
        "tier": "hot",
        "buckets": [{"size_gb": 100}]
    }], 10)
    assert result["status"] == "ZERO_USAGE"


# 3. Storage tier branches

@pytest.mark.parametrize("tier, expected", [
    ("hot", 2.5),
    ("cool", 1.5),
    ("archive", 0.5)
])
def test_all_valid_tiers(tier, expected):
    result = process_storage_tenants([{
        "account_active": True,
        "tier": tier,
        "buckets": [{"size_gb": 100}]
    }], 10)
    assert result["total_billed"] == expected


def test_unknown_tier():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "unknown",
        "buckets": [{"size_gb": 100}]
    }], 10)
    assert result["status"] == "ZERO_USAGE"


# 4. Bucket size branches

def test_zero_size_bucket():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 0}]
    }], 10)
    assert result["status"] == "ZERO_USAGE"


def test_negative_size_bucket():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": -10}]
    }], 10)
    assert result["status"] == "ZERO_USAGE"


def test_bucket_exactly_500_gb():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 500}]
    }], 10)
    assert result["total_billed"] == 12.5


def test_bucket_above_500_gb():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 600}]
    }], 10)
    assert result["total_billed"] == 13.5


# 5. Corrupted bucket branches

def test_corrupted_hot_bucket():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100, "corrupted": True}]
    }], 10)
    assert result["status"] == "ZERO_USAGE"


def test_corrupted_cool_bucket():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "cool",
        "buckets": [{"size_gb": 100, "corrupted": True}]
    }], 10)
    assert result["status"] == "ZERO_USAGE"


def test_corrupted_archive_bucket_breaks_loop():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "archive",
        "buckets": [
            {"size_gb": 100, "corrupted": True},
            {"size_gb": 200}
        ]
    }], 10)
    assert result["status"] == "ZERO_USAGE"


def test_non_corrupted_bucket():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100, "corrupted": False}]
    }], 10)
    assert result["total_billed"] == 2.5


# 6. Egress branches

def test_egress_exactly_100_gb():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100, "egress_gb": 100}]
    }], 10)
    assert result["total_billed"] == 2.5


def test_egress_above_100_gb():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100, "egress_gb": 150}]
    }], 10)
    assert result["total_billed"] == 6.5


# 7. Backup vault branches

def test_backup_enabled():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "has_backup_vault": True,
        "buckets": [{"size_gb": 100}]
    }], 10)
    assert result["total_billed"] == 12.5


def test_backup_disabled():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "has_backup_vault": False,
        "buckets": [{"size_gb": 100}]
    }], 10)
    assert result["total_billed"] == 2.5


# 8. Audit and billing status branches

def test_exactly_four_flagged_buckets():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [
            {"size_gb": 0},
            {"size_gb": 0},
            {"size_gb": 0},
            {"size_gb": 0}
        ]
    }], 10)
    assert result["status"] == "ZERO_USAGE"


def test_more_than_four_flagged_buckets():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [
            {"size_gb": 0},
            {"size_gb": 0},
            {"size_gb": 0},
            {"size_gb": 0},
            {"size_gb": 0}
        ]
    }], 10)
    assert result["status"] == "AUDIT_FLAGGED"


def test_billed_status():
    result = process_storage_tenants([{
        "account_active": True,
        "tier": "hot",
        "buckets": [{"size_gb": 100}]
    }], 10)
    assert result["status"] == "BILLED"


# 9. Replication latency branches

def test_empty_cluster_matrix():
    assert monitor_replication_latency([]) == "NO_DATA"


def test_cluster_with_empty_node_logs():
    assert monitor_replication_latency([[]]) == "SYNCED"


def test_latency_below_threshold():
    assert monitor_replication_latency([[100, 150]]) == "SYNCED"


def test_latency_exactly_200():
    assert monitor_replication_latency([[200, 200]]) == "SYNCED"


def test_single_high_latency():
    assert monitor_replication_latency([[250]]) == "SYNCED"


def test_high_latency_followed_by_normal():
    assert monitor_replication_latency([[250, 100, 250]]) == "SYNCED"


def test_two_consecutive_high_latencies():
    assert monitor_replication_latency([[250, 250]]) == "SYNC_LAG_ALERT"


def test_high_latency_across_multiple_nodes():
    assert monitor_replication_latency([
        [250],
        [100, 250, 250]
    ]) == "SYNC_LAG_ALERT"