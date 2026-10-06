#!/usr/bin/env python3
"""Independent 100-sentence Vietnamese-English code-switch route test.

This runner deliberately does NOT import benchmark_frozen, benchmark scripts,
repo gold files, or repo scoring utilities. Its only project dependency is the
public T0 normalizer; the route oracle is the separately hand-annotated
cases.jsonl next to this file.

Run from any directory:
    python /path/to/independent_codeswitch_100/run_independent.py
    python .../run_independent.py --json-out report.json
    python .../run_independent.py --show-passed
"""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from g2p_hamster.t0 import normalize
except Exception as exc:  # provide an actionable error instead of a traceback
    raise SystemExit(
        "Không import được g2p_hamster.t0. Hãy chạy script trong repo/venv có "
        f"cài g2p-hamster. Chi tiết: {type(exc).__name__}: {exc}"
    ) from exc

DATA = Path(__file__).with_name("cases.jsonl")
LEXICAL_CATS = {"word", "abbr", "acronym", "slang"}


_APOS = str.maketrans({"\u2019": "'", "\u02bc": "'", "\u2018": "'", "\u00b4": "'"})


def key(s: str) -> str:
    """NFC + casefold + chuẩn hóa dấu nháy để khớp surface không phụ thuộc
    kiểu apostrophe (nhãn "don't" khớp token "donʼt")."""
    return unicodedata.normalize("NFC", s).translate(_APOS).casefold()


def load_cases(path: Path) -> list[dict]:
    cases = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            case = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"JSON lỗi tại {path}:{line_no}: {exc}") from exc
        case["_line"] = line_no
        cases.append(case)

    errors = []
    ids = [c.get("id") for c in cases]
    texts = [c.get("text", "").strip() for c in cases]
    strata = Counter(c.get("stratum") for c in cases)
    # kiểm kết cấu 100 câu / 10 nhóm chỉ áp cho bộ chính; file khác
    # (cases_overlap_100.jsonl) chấp nhận nhóm lệch, thiếu một phía anchor.
    main_suite = path.resolve() == DATA.resolve()
    if len(ids) != len(set(ids)):
        errors.append("id bị trùng")
    if len(texts) != len(set(texts)):
        errors.append("câu đầu vào bị trùng")
    if main_suite:
        if len(cases) != 100:
            errors.append(f"cần đúng 100 câu, hiện có {len(cases)}")
        if len(strata) != 10 or any(n != 10 for n in strata.values()):
            errors.append(f"cần 10 nhóm, mỗi nhóm 10 câu; hiện có {dict(strata)}")
    for c in cases:
        if c.get("expected_sent_lang") not in ("mixed", None):
            errors.append(f"{c.get('id')}: expected_sent_lang phải là mixed hoặc null")
        cid = c.get("id", f"line {c['_line']}")
        anchors = c.get("anchors", [])
        routes = {a.get("route") for a in anchors}
        if main_suite and not {"vi", "en"}.issubset(routes):
            errors.append(f"{cid}: cần có ít nhất một anchor vi và một anchor en")
        if not anchors:
            errors.append(f"{cid}: không có anchor nào")
        seen = set()
        for a in anchors:
            if a.get("route") not in {"vi", "en"}:
                errors.append(f"{cid}: route anchor không hợp lệ: {a}")
            if a.get("confidence", "high") not in {"high", "medium"}:
                errors.append(f"{cid}: confidence phải là high hoặc medium: {a}")
            if not a.get("surface"):
                errors.append(f"{cid}: anchor thiếu surface: {a}")
            occ = int(a.get("occurrence", 1))
            a["occurrence"] = occ
            marker = (key(a.get("surface", "")), occ)
            if marker in seen:
                errors.append(f"{cid}: anchor lặp không phân biệt occurrence: {a}")
            seen.add(marker)
    if errors:
        raise SystemExit("Dữ liệu test không hợp lệ:\n- " + "\n- ".join(errors))
    return cases


def find_anchor(tokens: list[dict], anchor: dict) -> dict | None:
    wanted = key(anchor["surface"])
    matches = [t for t in tokens
               if t.get("cat") in LEXICAL_CATS and key(t.get("surface", "")) == wanted]
    occ = anchor.get("occurrence", 1)
    return matches[occ - 1] if 1 <= occ <= len(matches) else None


def evaluate(cases: list[dict]) -> dict:
    rows = []
    expected_route = Counter()
    confusion = Counter()
    by_stratum = defaultdict(lambda: Counter())
    by_confidence = defaultdict(lambda: Counter())
    total_anchors = found_anchors = correct_anchors = 0
    sent_expected = sent_correct = 0
    route_sentence_passes = full_sentence_passes = 0
    route_origin_divergences = 0

    for case in cases:
        try:
            ir = normalize(case["text"])
            error = None
        except Exception as exc:  # one bad input should not hide the other 99
            ir = {"tokens": [], "sent_lang": None, "read_string": None}
            error = f"{type(exc).__name__}: {exc}"

        anchor_rows = []
        route_pass = error is None
        for anchor in case["anchors"]:
            total_anchors += 1
            route = anchor["route"]
            confidence = anchor.get("confidence", "high")
            expected_route[route] += 1
            group_stats = by_stratum[case["stratum"]]
            group_stats[f"expected_{route}"] += 1
            confidence_stats = by_confidence[confidence]
            confidence_stats["expected"] += 1
            actual = find_anchor(ir["tokens"], anchor)
            if actual is None:
                route_pass = False
                group_stats["missing"] += 1
                confidence_stats["missing"] += 1
                anchor_rows.append({
                    "surface": anchor["surface"], "expected_route": route,
                    "confidence": confidence, "occurrence": anchor["occurrence"],
                    "status": "MISSING",
                })
                continue

            found_anchors += 1
            confidence_stats["found"] += 1
            actual_route = actual.get("route")
            actual_origin = actual.get("origin")
            confusion[(route, actual_route)] += 1
            group_stats["found"] += 1
            if actual_route == route:
                correct_anchors += 1
                group_stats["correct"] += 1
                confidence_stats["correct"] += 1
                status = "PASS"
            else:
                route_pass = False
                group_stats["wrong"] += 1
                confidence_stats["wrong"] += 1
                status = "WRONG_ROUTE"
            if actual_origin != actual_route:
                route_origin_divergences += 1
            anchor_rows.append({
                "surface": actual.get("surface"),
                "expected_route": route,
                "actual_route": actual_route,
                "confidence": confidence,
                "origin": actual_origin,
                "origin_differs_from_route": actual_origin != actual_route,
                "category": actual.get("cat"),
                "review": actual.get("review"),
                "occurrence": anchor["occurrence"],
                "status": status,
            })

        expected_lang = case.get("expected_sent_lang")
        actual_lang = ir.get("sent_lang")
        lang_ok = expected_lang is None or actual_lang == expected_lang
        if expected_lang is not None:
            sent_expected += 1
            sent_correct += int(lang_ok)
        if route_pass:
            route_sentence_passes += 1
        full_sentence_pass = route_pass and lang_ok
        if full_sentence_pass:
            full_sentence_passes += 1

        rows.append({
            "id": case["id"],
            "stratum": case["stratum"],
            "text": case["text"],
            "sent_lang_expected": expected_lang,
            "sent_lang_actual": actual_lang,
            "sent_lang_ok": lang_ok,
            "route_pass": route_pass,
            "full_sentence_pass": full_sentence_pass,
            "error": error,
            "anchors": anchor_rows,
            "read_string": ir.get("read_string"),
            "tokens": [
                {k: t.get(k) for k in ("surface", "cat", "route", "origin", "review", "verbal")}
                for t in ir.get("tokens", [])
            ],
        })

    denominator = total_anchors
    summary = {
        "suite": "independent_vi_en_codeswitch_route_test",
        "suite_version": "1.0",
        "case_count": len(cases),
        "anchor_count": total_anchors,
        "anchors_found": found_anchors,
        "anchors_missing": total_anchors - found_anchors,
        "anchors_correct": correct_anchors,
        "anchor_route_accuracy_including_missing": (
            correct_anchors / denominator if denominator else 0.0
        ),
        "anchor_route_accuracy_on_found_only": (
            correct_anchors / found_anchors if found_anchors else 0.0
        ),
        "route_sentence_pass_count": route_sentence_passes,
        "route_sentence_pass_rate": route_sentence_passes / len(cases) if cases else 0.0,
        "full_sentence_pass_count": full_sentence_passes,
        "full_sentence_pass_rate": full_sentence_passes / len(cases) if cases else 0.0,
        "route_origin_divergences": route_origin_divergences,
        "sent_lang_expected_count": sent_expected,
        "sent_lang_correct": sent_correct,
        "sent_lang_accuracy": sent_correct / sent_expected if sent_expected else None,
        "route_confusion": {
            expected: {
                actual: confusion[(expected, actual)]
                for actual in ("vi", "en", None)
            }
            for expected in ("vi", "en")
        },
        "by_confidence": {
            name: {
                "expected": stats["expected"],
                "found": stats["found"],
                "correct": stats["correct"],
                "wrong": stats["wrong"],
                "missing": stats["missing"],
                "accuracy_including_missing": (
                    stats["correct"] / stats["expected"] if stats["expected"] else 0.0
                ),
            }
            for name, stats in sorted(by_confidence.items())
        },
        "by_stratum": {
            name: {
                "expected_anchors": stats["expected_vi"] + stats["expected_en"],
                "found": stats["found"],
                "correct": stats["correct"],
                "wrong": stats["wrong"],
                "missing": stats["missing"],
                "accuracy_including_missing": (
                    stats["correct"] / (stats["expected_vi"] + stats["expected_en"])
                    if (stats["expected_vi"] + stats["expected_en"]) else 0.0
                ),
            }
            for name, stats in sorted(by_stratum.items())
        },
        "cases": rows,
    }
    return summary


def pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x * 100:.2f}%"


def print_report(report: dict, show_passed: bool = False, verbose: bool = False) -> None:
    print("Independent VI–EN code-switch routing test")
    print(f"Câu: {report['case_count']} | anchors: {report['anchor_count']} "
          f"(found {report['anchors_found']}, missing {report['anchors_missing']})")
    print("Route accuracy (missing tính là sai): "
          f"{report['anchors_correct']}/{report['anchor_count']} = "
          f"{pct(report['anchor_route_accuracy_including_missing'])}")
    print("Accuracy trên anchor tìm thấy: "
          f"{pct(report['anchor_route_accuracy_on_found_only'])}")
    print("Độ chắc nhãn:")
    for name, stats in report["by_confidence"].items():
        print(f"  {name:6} {stats['correct']}/{stats['expected']} = "
              f"{pct(stats['accuracy_including_missing'])} "
              f"(sai {stats['wrong']}, thiếu {stats['missing']})")
    print(f"Câu đạt toàn bộ anchor routes: {report['route_sentence_pass_count']}/"
          f"{report['case_count']} = {pct(report['route_sentence_pass_rate'])}")
    print(f"sent_lang đúng là mixed: {report['sent_lang_correct']}/"
          f"{report['sent_lang_expected_count']} = {pct(report['sent_lang_accuracy'])}")
    print(f"Câu đạt cả route lẫn sent_lang: {report['full_sentence_pass_count']}/"
          f"{report['case_count']} = {pct(report['full_sentence_pass_rate'])}")
    print(f"Anchor có origin khác route (chỉ để chẩn đoán): {report['route_origin_divergences']}")
    print("\nTheo nhóm:")
    for name, stats in report["by_stratum"].items():
        print(f"  {name:24} {stats['correct']:>3}/{stats['expected_anchors']:<3} "
              f"{pct(stats['accuracy_including_missing'])} "
              f"(sai {stats['wrong']}, thiếu {stats['missing']})")

    route_failures = [c for c in report["cases"] if not c["route_pass"]]
    if route_failures:
        print("\nAnchor bị thiếu hoặc route sai:")
        for case in route_failures:
            print(f"\n[{case['id']} | {case['stratum']}] {case['text']}")
            if case["error"]:
                print(f"  EXCEPTION: {case['error']}")
            for a in case["anchors"]:
                if a["status"] != "PASS":
                    print(f"  {a['surface']!r} ({a['confidence']}): "
                          f"expected={a['expected_route']}, "
                          f"actual={a.get('actual_route', 'MISSING')}, "
                          f"origin={a.get('origin')}, review={a.get('review')}")
            if verbose:
                print(f"  tokens: {case['tokens']}")

    lid_failures = [c for c in report["cases"] if not c["sent_lang_ok"]]
    if lid_failures:
        ids = ", ".join(f"{c['id']}={c['sent_lang_actual']}" for c in lid_failures)
        print(f"\nsent_lang không phải 'mixed' ở {len(lid_failures)} câu: {ids}")
        if verbose:
            for case in lid_failures:
                print(f"  [{case['id']}] {case['text']}")
                if case["route_pass"]:
                    print(f"    tokens: {case['tokens']}")
    elif show_passed:
        print("\nTất cả 100 câu đạt cả route lẫn sent_lang.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA,
                        help="JSONL test set (mặc định: cases.jsonl kế bên script)")
    parser.add_argument("--json-out", type=Path,
                        help="ghi toàn bộ kết quả và trace token ra JSON")
    parser.add_argument("--show-passed", action="store_true",
                        help="in thông báo khi cả bộ đạt")
    parser.add_argument("--verbose", action="store_true",
                        help="in cả token trace cho mọi câu sent_lang lệch")
    parser.add_argument("--route-only", action="store_true",
                        help="exit code chỉ phụ thuộc route anchor; vẫn in metric sent_lang riêng")
    args = parser.parse_args()

    cases = load_cases(args.data)
    report = evaluate(cases)
    print_report(report, args.show_passed, args.verbose)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\nJSON chi tiết: {args.json_out}")
    if args.route_only:
        return 0 if report["anchors_missing"] == 0 and report["route_sentence_pass_count"] == report["case_count"] else 1
    return 0 if report["anchors_missing"] == 0 and report["full_sentence_pass_count"] == report["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
