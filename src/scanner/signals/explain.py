from __future__ import annotations

from typing import Any

# Centralized explanation builder to keep routes clean.


def explain_ordering(f: dict[str, Any]) -> tuple[str, list[str]]:
    pairs = f.get("pairs") or []
    msg = (
        "A subset of adjacent transactions targeting the same contract/address exhibits divergent outcomes "
        "in close proximity. This pattern often correlates with order-dependent reads/writes and contention "
        "on shared state segments, becoming visible under higher throughput."
    )
    actions = [
        "For dApps: reduce shared-state writes; adopt idempotent patterns; avoid implicit ordering assumptions.",
        "For dApps: isolate critical writes; consider batching with explicit sequencing safeguards.",
        "For ops: monitor revert density around the affected target; correlate with peak load windows.",
    ]
    evidence = {"adjacent_pairs": pairs[:20], "count": len(pairs)}
    return msg, actions, evidence


def explain_conflict(f: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    failures = int(f.get("failures") or 0)
    ratio = float(f.get("ratio") or 0.0)
    msg = (
        "This block shows elevated revert/failure density. When failures cluster, it can indicate contention "
        "patterns (shared nonces/resources), unstable contract execution paths, or overloaded state hotspots."
    )
    actions = [
        "For dApps: add pre-flight checks; reduce nonce contention; handle optimistic failures gracefully.",
        "For ops: correlate with RPC errors and mempool bursts; track per-target revert spikes.",
    ]
    evidence = {"failures": failures, "ratio": ratio, "sample_txs": f.get("sample_txs") or []}
    return msg, actions, evidence


def explain_hot_state(f: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    top = f.get("top") or []
    msg = (
        "Repeated touches to the same execution targets and/or event topics suggest concentrated pressure "
        "on a small subset of state. Such hotspots can degrade performance and amplify cross-tx interference."
    )
    actions = [
        "For dApps: shard state; spread writes; avoid single-key counters; use more granular storage layout.",
        "For ops: watch these hotspots during peak load; consider alerting on persistent concentration.",
    ]
    evidence = {"top_candidates": top}
    return msg, actions, evidence


def explain_dependency(f: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    groups = f.get("groups") or []
    msg = (
        "Multiple transactions appear coupled through shared targets/topics, indicating implicit resource sharing. "
        "Under load, this coupling increases the probability of surprising execution interference and non-obvious "
        "failure cascades."
    )
    actions = [
        "For dApps: reduce implicit coupling; avoid shared global state; separate flows across distinct storage areas.",
        "For ops: correlate group size with revert bursts; prioritize investigation of the largest clusters.",
    ]
    evidence = {"groups": groups}
    return msg, actions, evidence
