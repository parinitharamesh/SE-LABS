
import math
import re


def parse_storage_quota(quota_str):
    """
    Parses storage quota into Gigabytes (GB).
    Supports MB, GB and TB.
    Returns None for invalid inputs.
    """
    if not isinstance(quota_str, str):
        return None

    cleaned = quota_str.strip().upper()

    match = re.fullmatch(r"(\d+)(MB|GB|TB)", cleaned)

    if not match:
        return None

    try:
        value = int(match.group(1))
        unit = match.group(2)

        multipliers = {
            "MB": 0.001,
            "GB": 1.0,
            "TB": 1000.0
        }

        gb_total = value * multipliers[unit]

        if not math.isfinite(gb_total):
            return None

        return f"Quota: {gb_total:.2f} GB"

    except (ValueError, OverflowError):
        return None


def compute_compression_ratio(size_metric_str):
    """
    Computes compression ratio:
    raw_bytes / compressed_bytes.
    Returns None for invalid inputs.
    """
    if not isinstance(size_metric_str, str):
        return None

    parts = size_metric_str.split(':')

    if len(parts) != 2:
        return None

    try:
        raw_bytes = float(parts[0].strip())
        comp_bytes = float(parts[1].strip())

        if not math.isfinite(raw_bytes) or not math.isfinite(comp_bytes):
            return None

        if raw_bytes < 0 or comp_bytes <= 0:
            return None

        ratio = raw_bytes / comp_bytes

        if not math.isfinite(ratio):
            return None

        return round(ratio, 2)

    except (ValueError, TypeError, ZeroDivisionError, OverflowError):
        return None


def lookup_bandwidth_tier_rate(tier_descriptor):
    """
    Looks up egress rate using the first three letters
    of HOT, COLD or ARCHIVE.
    Returns None for invalid inputs.
    """
    if not isinstance(tier_descriptor, str):
        return None

    cleaned = tier_descriptor.strip().upper()

    if len(cleaned) < 3:
        return None

    prefix = cleaned[:3]

    tier_rates = {
        "HOT": 0.08,
        "COL": 0.05,
        "ARC": 0.02
    }

    return tier_rates.get(prefix)


def main():
    print("==== Running parse_storage_quota ====")
    q_input = input("Enter quota (e.g. 500MB, 10GB, 2TB): ")
    result = parse_storage_quota(q_input)
    print(result if result is not None else "Invalid quota input.")

    print("\n==== Running compute_compression_ratio ====")
    c_input = input("Enter raw:compressed bytes (e.g. 1024:256): ")
    result = compute_compression_ratio(c_input)
    print("Compression Ratio:", result if result is not None else "Invalid size metric.")

    print("\n==== Running lookup_bandwidth_tier_rate ====")
    t_input = input("Enter tier descriptor (e.g. HOT_TIER, COLD, ARCHIVE): ")
    result = lookup_bandwidth_tier_rate(t_input)
    print("Rate per GB: $", result if result is not None else "Invalid tier descriptor.")


if __name__ == "__main__":
    main()
