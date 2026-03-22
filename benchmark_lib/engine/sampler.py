from __future__ import annotations

import random
from collections import defaultdict

from ..utils.types import NormalizedSample


MODE_SIZES = {
    "quick": 100,
    "half": 1500,
    "full": 6000,
}

TARGET_RATIOS = {
    "easy": 0.30,
    "medium": 0.50,
    "hard": 0.20,
}

TARGET_DOMAINS = ["code", "logic", "knowledge", "math"]
MAX_DATASETS_PER_DOMAIN = 2


def _allocate_counts(total: int, buckets: list[str]) -> dict[str, int]:
    if not buckets:
        return {}
    base = total // len(buckets)
    rem = total % len(buckets)
    out: dict[str, int] = {b: base for b in buckets}
    for b in buckets[:rem]:
        out[b] += 1
    return out


def _take_by_difficulty(
    candidates: list[NormalizedSample],
    target_size: int,
    rng: random.Random,
) -> list[NormalizedSample]:
    by_diff: dict[str, list[NormalizedSample]] = defaultdict(list)
    for s in candidates:
        by_diff[s.difficulty].append(s)

    for bucket in by_diff.values():
        rng.shuffle(bucket)

    want_counts = {k: int(round(target_size * v)) for k, v in TARGET_RATIOS.items()}
    while sum(want_counts.values()) > target_size:
        want_counts["medium"] -= 1
    while sum(want_counts.values()) < target_size:
        want_counts["medium"] += 1

    selected: list[NormalizedSample] = []
    selected_ids: set[str] = set()

    for diff in ["easy", "medium", "hard"]:
        bucket = by_diff.get(diff, [])
        take = min(want_counts[diff], len(bucket))
        chosen = bucket[:take]
        selected.extend(chosen)
        selected_ids.update(s.id for s in chosen)

    if len(selected) < target_size:
        remaining = [s for s in candidates if s.id not in selected_ids]
        rng.shuffle(remaining)
        selected.extend(remaining[: target_size - len(selected)])

    rng.shuffle(selected)
    return selected[:target_size]


def _pick_two_datasets_per_domain(samples: list[NormalizedSample]) -> dict[str, list[str]]:
    grouped: dict[str, dict[str, int]] = defaultdict(dict)
    for s in samples:
        if s.domain not in TARGET_DOMAINS:
            continue
        grouped[s.domain][s.dataset] = grouped[s.domain].get(s.dataset, 0) + 1

    selected: dict[str, list[str]] = {}
    for domain in TARGET_DOMAINS:
        ds_counts = grouped.get(domain, {})
        ranked = sorted(ds_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        selected[domain] = [name for name, _ in ranked[:MAX_DATASETS_PER_DOMAIN]]
    return selected


def stratified_sample(samples: list[NormalizedSample], mode: str, seed: int) -> list[NormalizedSample]:
    if mode not in MODE_SIZES:
        raise ValueError(f"Unknown mode: {mode}")

    rng = random.Random(seed)
    target_size = min(MODE_SIZES[mode], len(samples))
    picked_by_domain = _pick_two_datasets_per_domain(samples)

    allowed_pairs = {
        (domain, ds)
        for domain, datasets in picked_by_domain.items()
        for ds in datasets
    }
    filtered = [s for s in samples if (s.domain, s.dataset) in allowed_pairs]

    if not filtered:
        return []

    domains = [d for d in TARGET_DOMAINS if picked_by_domain.get(d)]
    domain_quota = _allocate_counts(min(target_size, len(filtered)), domains)

    by_domain_dataset: dict[str, dict[str, list[NormalizedSample]]] = defaultdict(lambda: defaultdict(list))
    for s in filtered:
        by_domain_dataset[s.domain][s.dataset].append(s)

    for dmap in by_domain_dataset.values():
        for bucket in dmap.values():
            rng.shuffle(bucket)

    selected: list[NormalizedSample] = []
    selected_ids: set[str] = set()

    for domain in domains:
        datasets = picked_by_domain[domain]
        ds_quota = _allocate_counts(domain_quota[domain], datasets)

        for ds in datasets:
            candidates = by_domain_dataset[domain][ds]
            take = min(ds_quota[ds], len(candidates))
            if take <= 0:
                continue
            chosen = _take_by_difficulty(candidates, take, rng)
            selected.extend(chosen)
            selected_ids.update(s.id for s in chosen)

    final_target = min(target_size, len(filtered))
    if len(selected) < final_target:
        remaining = [s for s in filtered if s.id not in selected_ids]
        rng.shuffle(remaining)
        selected.extend(remaining[: final_target - len(selected)])

    rng.shuffle(selected)
    return selected[:final_target]
