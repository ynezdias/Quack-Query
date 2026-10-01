"""Expanded regression benchmark: python -m src.evaluate_expanded [--answers]."""
import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from statistics import mean
from pathlib import Path
from src.knowledge import ROOT, read_manifest
from src.rag import retrieve_chunks, generate_response, contextualize

DATASET = ROOT / "eval/expanded_questions.json"


def retrieval_metrics(expected, chunks):
    names = [c["metadata"]["filename"] for c in chunks]
    required = set(expected)
    return {"retrieved": names,
            "source_recall": len(required & set(names)) / len(required) if required else None,
            "all_sources": required.issubset(names) if required else None,
            "reciprocal_rank": next((1 / (i + 1) for i, n in enumerate(names) if n in required), 0) if required else None}


def summarize(rows):
    summary = {"rows": len(rows)}
    for key in ("source_recall", "all_sources", "reciprocal_rank", "status_correct"):
        values = [r[key] for r in rows if r.get(key) is not None]
        summary[key] = {"count": len(values), "mean": mean(values) if values else None}
    summary["generation_errors"] = sum("error" in r for r in rows)
    return summary


def run(answers=False, ids=None, top_k=8, delay=20, output=None):
    raw = DATASET.read_bytes()
    cases = json.loads(raw)
    if ids:
        requested = set(ids.split(","))
        available = {c["id"] for c in cases}
        if requested - available:
            raise ValueError(f"Unknown case IDs: {sorted(requested - available)}")
        cases = [c for c in cases if c["id"] in requested]
    corpora = sorted({c["corpus"] for c in cases})
    for corpus in corpora:
        retrieve_chunks("warmup", corpus=corpus, top_k=top_k)
    manifest = read_manifest()
    report = {"created_at": datetime.now(timezone.utc).isoformat(),
              "dataset_sha256": hashlib.sha256(raw).hexdigest(),
              "code_hashes": {name: hashlib.sha256((ROOT / "src" / name).read_bytes()).hexdigest()
                              for name in ("rag.py", "retrieval.py", "evaluate_expanded.py")},
              "corpora": {c: manifest[c] for c in corpora},
              "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
              "top_k": top_k, "answer_evaluation": answers, "case_count": len(cases),
              "limitations": "Regression cases, not held-out accuracy. Source presence is not evidence sufficiency. Status matching is not factual correctness. Review answers against reference_answer manually, including entailment, completeness, units, scope and contradictions.",
              "results": []}
    destination = Path(output) if output else ROOT / "eval/expanded-results.json"
    last_request = None
    for case in cases:
        for mode in ("semantic", "hybrid"):
            history = case.get("history", [])
            start = time.perf_counter()
            chunks = retrieve_chunks(contextualize(case["question"], history), corpus=case["corpus"], mode=mode, top_k=top_k)
            row = {**case, "mode": mode, "retrieval_seconds": time.perf_counter() - start,
                   **retrieval_metrics(case["expected_sources"], chunks)}
            if answers and mode == "hybrid":
                if last_request is not None:
                    time.sleep(max(0, delay - (time.perf_counter() - last_request)))
                last_request = time.perf_counter()
                try:
                    response = generate_response(case["question"], chunks, history=history)
                    row["response"] = response
                    row["status_correct"] = response["status"] == case["expected_status"]
                    row["review_context"] = chunks
                    row["manual_review"] = {"factual_correctness": None, "citation_entailment": None,
                                             "completeness": None, "notes": "Not reviewed"}
                except Exception as exc:
                    row["error"] = type(exc).__name__
                    row["status_correct"] = False
            report["results"].append(row)
        report["completed_cases"] = len(report["results"]) // 2
        report["summary"] = {corpus: {mode: summarize([r for r in report["results"] if r["corpus"] == corpus and r["mode"] == mode])
                                      for mode in ("semantic", "hybrid")} for corpus in corpora}
        report["by_category"] = {category: summarize([r for r in report["results"] if r["category"] == category and r["mode"] == "hybrid"])
                                 for category in sorted({c["category"] for c in cases})}
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(json.dumps(report, indent=2), encoding="utf-8")
        temporary.replace(destination)
        print(f"Evaluated {case['id']}", flush=True)
    print(json.dumps(report["summary"], indent=2))
    print(f"Saved {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answers", action="store_true")
    parser.add_argument("--ids", help="Comma-separated case IDs for a targeted run")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--delay", type=float, default=20)
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.top_k < 1 or args.delay < 0:
        parser.error("top-k must be positive and delay nonnegative")
    run(args.answers, args.ids, args.top_k, args.delay, args.output)
