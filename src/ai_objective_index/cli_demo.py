from __future__ import annotations

import argparse

from .scoring import score_object
from .seed_loader import load_sample_index, load_source_traces
from .store import ObjectiveIndexStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a read-only AI Objective Index demo search.")
    parser.add_argument("query", help="Objective query to search and score.")
    parser.add_argument("--domain", default=None, help="Optional AOI domain filter.")
    args = parser.parse_args()

    objects = load_sample_index()
    traces = load_source_traces()
    store = ObjectiveIndexStore(objects, traces)

    candidates = store.search_objects(args.query, domain=args.domain, limit=10)
    scored = [
        (
            candidate,
            score_object(
                candidate,
                query=args.query,
                traces=store.get_traces(candidate.object_id),
                constraints={"requires_documented_terms": True},
            ),
        )
        for candidate in candidates
    ]
    scored.sort(key=lambda item: item[1].objective_score, reverse=True)

    print("AI Objective Index Package 1 CLI demo")
    print(f"Query: {args.query}")
    print("Read-only output: no purchase, booking, payment, login, email, or contract execution.")
    print()

    for rank, (candidate, score) in enumerate(scored[:5], start=1):
        print(f"{rank}. {candidate.name} ({candidate.object_id})")
        print(f"   objective_score: {score.objective_score}")
        print(f"   status: {score.status}")
        print(f"   rank_reason: {'; '.join(score.rank_reason)}")
        missing = ", ".join(score.missing_fields[:5]) if score.missing_fields else "none"
        print(f"   missing_fields: {missing}")
        print()


if __name__ == "__main__":
    main()

