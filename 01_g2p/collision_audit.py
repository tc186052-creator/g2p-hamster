# -*- coding: utf-8 -*-
"""collision_audit.py — THỰC THI điều 7 (realization-collision audit) cho tiếng Việt.

VÒNG 5 (theo báo cáo review v5 — V5-01/02/04/05):
  1. Miền sinh PHÂN LỚP, core theo NGỮ CẢNH (is_core): yê chỉ khi không onset hoặc
     sau qu; ây nhận coda y; ng mất e/ê (ngh phụ trách). Kiểm ĐỘC LẬP accept/reject
     (CORE_ACCEPT/CORE_REJECT) — sai → FAIL.
  2. Spellings sinh bằng render canonical (renderer hợp nhất chữ i dùng chung của
     nhánh gi — V5-02) rồi parse ngược; mỗi chính tả 1 đường parse.
  3. Giải thích PHÂN TẦNG: identity (parts vốn giống) → approved → proposal →
     unexplained; composition XÁC ĐỊNH theo thứ tự catalog, mỗi bước phải hợp lệ và
     BẢO TOÀN record phát âm (xem inventory._explain_parts).
  4. Status MỘT NƠI (compute_status): contrast_fail hoặc core_fail → FAIL; dùng
     chung cho JSON/Markdown/stdout/exit (V5-05).

VÒNG 6 (theo báo cáo review vòng 6 — §5, §8, §9.1): CORE THEO CĂN CỨ ĐỘC LẬP.
  is_core() ngữ cảnh KHÔNG đủ ("câi/mấi/bêo" vẫn lọt). Core = is_core(ngữ cảnh)
  ∩ ATTESTED trong bảng âm tiết pin từ corpus IR tầng 1 (nguồn + sha256 + phiên
  bản — xem 02_data/core_domain/; bảng KHÔNG sinh từ parser). Dạng core-ngữ-cảnh
  nhưng không attested → lớp "ext" (miền mở rộng/thử nghiệm): giữ trong miền sinh,
  KHÔNG gate, KHÔNG đòi duyệt đồng âm. Gate (≥2 core-attested) giờ chỉ còn cặp
  chính tả thật cùng chuỗi âm vị — phạm vi hữu hạn minh bạch cho xét duyệt scope.
Ca reviewer câi/mấi/bêo/buâi/buây → DOMAIN_MUST_NOT (regression, không phải
held-out); cây/mấy/bêu… → DOMAIN_MUST_ATTEST. Vi phạm → FAIL.

VÒNG 6.5 (theo hậu kiểm v14 — R14-01/R14-02, §6):Boundary scope QD57 EXACT và
fingerprint phủ logic scope.
  1. R14-01: scope_exclusion_status so khớp EXACT NFC+lower GIỮ dấu thanh trên
     thành viên máy đọc (excluded_members/protected_members trong ledger, pin từ
     đáp án reviewer qd57/scope_expected_members_qd57.json) — KHÔNG còn phân tích
     văn xuôi `protected` bằng tìm chuỗi con (lỗi cũ: chếc⊂chếch, níc⊂ních,
     tíc⊂tích làm cả hai phía trả None). 39 subject trả trạng thái có cấu trúc,
     37 protected trả None; uppercase/NFD cùng kết quả.
  2. scope_boundary_check(): kiểm nhất quán ledger↔boundary thực chạy cho đủ 76
     thành viên — lệch → FAIL exit≠0, không còn PASS chỉ vì có tên cặp trong ledger.
  3. R14-02: scope_policy_hash gắn ledger hiệu lực (bytes) + đáp án thành viên pin
     + source hash loader/validator/boundary/status — đổi dữ liệu quyết định HOẶC
     logic scope phải làm hash đổi; hash này ghi vào report và gộp vào
     domain_config_hash. Probe mutation trên bản sao riêng: test_scope_policy.py.

VÒNG 6.2 (theo review R61-01/02/03): builder đếm TOKEN NGUYÊN DẠNG (không tách —
xem build_core_domain.py); domain_config_hash phủ SNAPSHOT RUNTIME classifier +
source hash (R61-02); scope doc sinh TỰ ĐỘNG từ JSON pin (gen_rule_scope.py —
R61-03). Số nhóm gate báo theo dữ liệu mới, không giữ số vòng trước.

Nhóm = các chính tả khác nhau cùng chuỗi semantic ID GỒM tone. Kèm kiểm các cặp
SYLLABLE_LEVEL_CONTRASTS (tai≠tay, tui≠tuy…) PHẢI khác chuỗi.

Output: 02_data/collision/dieu7_bao_cao.json + .md (có dòng Status tổng thể —
vòng 6 §8.1), stdout tổng kết, exit 1 FAIL, 2 PENDING_APPROVAL, 0 PASS.
Chạy:  cd 02_hamster_G2P && 03_vendor/venv_vig2p/bin/python 01_g2p/collision_audit.py
"""
import hashlib
import json
import sys
import unicodedata as U
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inventory  # noqa: E402
import vi_rules as R  # noqa: E402

OUT = HERE.parent / "02_data" / "collision"
QD57_EXCLUSIONS = OUT / "qd57_scope_exclusions.json"
QD57_EXPECTED_MEMBERS = OUT / "qd57" / "scope_expected_members_qd57.json"

TONE_IDS = ["TONE_NGANG", "TONE_HUYEN", "TONE_SAC", "TONE_HOI", "TONE_NGA", "TONE_NANG"]

# ------------------------------------------------------- miền chính tả lõi (F06, V5-01)
# onset → chữ nguyên âm ĐẦU của vần được phép (chính tả bổ túc vi; KHÔNG phải biến
# thể tự do — "ghá"/"nghá"/"cê"/"gé" là tổ hợp stress, không phải chính tả lõi).
# V5-01: ng KHÔNG được e/ê (ngh bổ túc front — "nge"/"ngê" không phải chính tả lõi).
CORE_ONSET_FIRST = {
    "c": set("aăâoôơuư"),        # k bổ túc trước front
    "k": set("eêiy"),
    "g": set("aăâoôơuư"),        # gh bổ túc trước front
    "gh": set("eêiy"),
    "ng": set("aăâoôơuư"),       # e,ê,i,y → ngh (V5-01: bỏ e/ê khỏi ng)
    "ngh": set("eêiy"),
}
# coda chính tả lõi: KHÔNG có "k" (k-coda chỉ từ mượn — nhóm ngoại lai)
CORE_TAILS = {t for t in R.CODA_MAP if t != "k"}


def is_core(parts):
    """(onset, glide_letter, form, tail) → True nếu chính tả thuộc lớp lõi.

    V5-01 — ràng buộc theo NGỮ CẢNH, không blacklist toàn form:
      - "yê" trực tiếp (không glide) chỉ lõi khi KHÔNG có onset (yên/yếu/yếm/yêu)
        hoặc sau "qu" (quyên/quyết/quyền — qu mang glide ngầm, gl vẫn rỗng);
        "tyê"/"myê"… không phải chính tả lõi.
      - "ya" trực tiếp bị loại (mỹa — không lõi; khuya là composite uya có glide).
      - coda "y" chỉ sau form "a" (tay, ngoay) và "â" (mây, cây, đấy — V5-01;
        "ôi/ôy" là tổ hợp stress).
      - form "y" bare + coda bị loại (tím không phải "tym").
      - c/k + glide 'o' bị loại: chính tả lõi viết 'qu' (coa/koa → qua; vòng 5).
    """
    onset, gl, form, tail = parts
    if tail not in CORE_TAILS:
        return False
    if form == "ya" and not gl:
        return False
    if form == "yê" and not gl and onset not in ("", "qu"):
        return False
    if form == "y" and tail and not gl:
        return False
    if tail == "y" and form not in ("a", "â"):
        return False
    if gl == "o" and onset in ("c", "k"):
        return False        # c/k + glide o viết bằng 'qu' ở lớp lõi (coa/koa → qua)
    if onset in CORE_ONSET_FIRST:
        first = gl or (form[0] if form else "")
        if first not in CORE_ONSET_FIRST[onset]:
            return False
    return True


# Kiểm ĐỘC LẬP miền core (V5-01): tập từ thật phải được nhận; tổ hợp ngoài chính tả
# phải bị loại. KHÔNG lấy output generator làm đáp án — chấp nhận/loại tường minh do
# người duyệt yêu cầu; vi phạm → FAIL.
CORE_ACCEPT = [
    "yên", "yến", "yếm", "yêu", "quyên", "quyết", "quyền", "mây", "cây", "tây",
    "đấy", "nghe", "buồm", "muỗm", "khuỷu", "gìn", "giêng", "giết", "tuy", "thúy",
    "huy", "khoét", "xuất", "khuya", "nga", "ngoan", "ngoại",
]
CORE_REJECT = [
    "nge", "ngê", "ngha", "gha", "ghá", "nghá", "cê", "gé", "ka", "mỹa", "mya",
    "ak", "ek", "tym", "tyên", "coa", "koa", "coác",
]


def core_acceptance_check():
    """Trả về list lỗi (rỗng = PASS): từng từ được parse rồi hỏi is_core — kiểm
    độc lập khỏi miền sinh (không dùng output generator làm đáp án)."""
    errs = []
    for w in CORE_ACCEPT:
        sk, _ = R.strip_tone(w)
        p = R.parse_skeleton(sk)
        if p is None:
            errs.append((w, "parse lỗi nhưng nằm trong CORE_ACCEPT"))
        elif not is_core(p):
            errs.append((w, f"từ thật phải thuộc core (parts={p})"))
    for w in CORE_REJECT:
        sk, _ = R.strip_tone(w)
        p = R.parse_skeleton(sk)
        if p is None:
            errs.append((w, "parse lỗi — dùng từ parse được cho probe reject"))
        elif is_core(p):
            errs.append((w, f"ngoài chính tả lõi nhưng được nhận core (parts={p})"))
    return errs


# ------------------------------------------------- căn cứ miền core ĐỘC LẬP (vòng 6)
# Bảng âm tiết pin từ corpus IR tầng 1 (build_core_domain.py sinh, provenance kèm
# sha256 nguồn + sha256 artifact). Audit KHÔNG đọc corpus — đọc bảng đã pin, kiểm
# hash từng lần chạy. ATTEST_MIN_FREQ=2: lọc typo đơn lẻ ("câi" gặp 1 lần trong
# 16,5 triệu âm tiết); con số và giới hạn được ghi trong provenance + scope doc.
CORE_DOMAIN_DIR = HERE.parent / "02_data" / "core_domain"
ATTEST_MIN_FREQ = 2


def load_attestation():
    """(vocab dict dạng token→freq, provenance dict). Báo lỗi nếu hash lệch provenance."""
    tsv = CORE_DOMAIN_DIR / "vi_syllable_vocab.tsv"
    prov_path = CORE_DOMAIN_DIR / "core_domain_provenance.json"
    if not tsv.exists() or not prov_path.exists():
        raise SystemExit("thiếu 02_data/core_domain/ — chạy 01_g2p/build_core_domain.py")
    prov = json.loads(prov_path.read_text(encoding="utf-8"))
    h = hashlib.sha256(tsv.read_bytes()).hexdigest()
    if h != prov.get("sha256_vocab"):
        raise SystemExit(f"hash vi_syllable_vocab.tsv lệch provenance: {h}")
    vocab = {}
    for line in tsv.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        syl, n = line.split("\t")
        vocab[syl] = int(n)
    return vocab, prov


def _member_sets(e):
    """Tập thành viên máy đọc của một entry ledger: exact NFC+lower, GIỮ dấu thanh
    (R14-01). Văn xuôi subject/protected/reason KHÔNG bao giờ dùng làm tập thành viên."""
    exc = {U.normalize("NFC", m).lower() for m in e.get("excluded_members", [])}
    prot = {U.normalize("NFC", m).lower() for m in e.get("protected_members", [])}
    return exc, prot


def load_scope_exclusions(path=None):
    """QD57-2026-10-02: ledger 38 giới hạn scope v1 (reviewer phán quyết per-group,
    chủ dự án chấp thuận 02/10). Trả về (policy dict, dict pair_key → entry).
    Pair key = 2 spelling NFC-lower đã sort. Ranh giới nằm trong _doc/scope của
    file: giới hạn ĐÚNG ĐỐI TƯỢNG (subject), phía protected không bị loại, KHÔNG
    phải giấy phép fold/spell mới, KHÔNG tự phục hồi dấu/đổi route/ghép tách token
    (QD57 §4). File pin bằng sha256 trong domain_config_hash (R61-02).

    Vòng 6.5 (R14-01): mỗi entry PHẢI có thành viên máy đọc excluded_members/
    protected_members phủ đúng pair, không giao; cross-check TỪNG cặp với đáp án
    regression pin qd57/scope_expected_members_qd57.json — thiếu/lệch → SystemExit
    (ledger hỏng không được đi tiếp thành audit PASS)."""
    p = path or QD57_EXCLUSIONS
    if not p.exists():
        raise SystemExit(f"thiếu {p} — pin hồ sơ QD57 (02_data/collision/qd57/) "
                         "trước khi chạy audit")
    data = json.loads(p.read_text(encoding="utf-8"))
    excl = {}
    for e in data["exclusions"]:
        key = tuple(sorted(U.normalize("NFC", w).lower() for w in e["pair"]))
        exc, prot = _member_sets(e)
        if not exc and not prot:
            raise SystemExit(f"entry {key}: thiếu thành viên máy đọc (R14-01) — "
                             "ledger phải có excluded_members/protected_members")
        if exc & prot:
            raise SystemExit(f"entry {key}: thành viên vừa excluded vừa protected "
                             f"{sorted(exc & prot)}")
        if exc | prot != set(key):
            raise SystemExit(f"entry {key}: thành viên máy đọc không phủ đúng pair "
                             f"(excluded {sorted(exc)} / protected {sorted(prot)})")
        excl[key] = e
    if len(excl) != data["n_excluded"]:
        raise SystemExit(f"ledger QD57 lệch: {len(excl)} pair ≠ n_excluded "
                         f"{data['n_excluded']}")
    # cross-check đáp án regression pin (nguồn quyết đã giao — hậu kiểm v14 §3)
    if not QD57_EXPECTED_MEMBERS.exists():
        raise SystemExit(f"thiếu {QD57_EXPECTED_MEMBERS} — đáp án thành viên pin "
                         "phải đi cùng ledger QD57")
    exp = json.loads(QD57_EXPECTED_MEMBERS.read_text(encoding="utf-8"))
    exp_map = {tuple(sorted(U.normalize("NFC", w).lower() for w in x["pair"])): x
               for x in exp["entries"]}
    if exp_map.keys() != excl.keys():
        raise SystemExit("đáp án thành viên pin không khớp bộ cặp của ledger QD57")
    for key, x in exp_map.items():
        exc, prot = _member_sets(excl[key])
        exp_exc = {U.normalize("NFC", m).lower() for m in x["excluded_members"]}
        exp_prot = {U.normalize("NFC", m).lower() for m in x["protected_members"]}
        if exc != exp_exc or prot != exp_prot:
            raise SystemExit(f"entry {key}: thành viên ledger lệch đáp án pin "
                             f"(ledger {sorted(exc)}/{sorted(prot)} ≠ pin "
                             f"{sorted(exp_exc)}/{sorted(exp_prot)})")
    return data, excl


def scope_exclusion_status(word):
    """Trạng thái giới hạn scope v1 của MỘT chính tả (QD57-2026-10-02, chủ dự án
    chấp thuận). Trả None khi từ không thuộc nhóm giới hạn nào hoặc là phía
    `protected` (không bị quyết định này loại). Ngược lại trả dict có cấu trúc —
    TÍN HIỆU cho tầng tiêu thụ (fase D) để trả trạng thái không hỗ trợ/chưa phân
    giải theo contract, KHÔNG phải lệnh phục hồi dấu/đổi route/ghép tách token và
    KHÔNG phải giấy phép fold/spell mới (QD57 §4).

    Vòng 6.5 (R14-01): so khớp EXACT NFC+lower GIỮ dấu thanh trên thành viên máy
    đọc của ledger — KHÔNG phân tích văn xuôi (lỗi cũ: tìm chuỗi con trong
    `protected` làm chếc/níc/tíc lọt vì là chuỗi con của chếch/ních/tích).
    Uppercase/NFD cho cùng kết quả vì normalize trước khi so; tue/tuê có cả hai
    phía trong excluded_members nên cả hai trả trạng thái."""
    w = U.normalize("NFC", word).lower()
    qd57, exclusions = load_scope_exclusions()
    for pair, e in sorted(exclusions.items()):
        if w in pair:
            exc, prot = _member_sets(e)
            if w in prot:
                return None
            if w in exc:
                return {"status": "scope_excluded_v1", "policy_id": qd57["policy_id"],
                        "pair": list(pair), "subject": e["subject"],
                        "protected": e["protected"], "reason": e["reason"]}
            # không thể tới đây sau validate của load_scope_exclusions — phòng thủ
            raise SystemExit(f"scope ledger lệch: {w!r} thuộc pair {list(pair)} "
                             "nhưng không nằm ở tập thành viên nào")
    return None


def scope_boundary_check():
    """Kiểm nhất quán ledger↔boundary thực chạy (hậu kiểm v14 §6.2, R14-01): từng
    thành viên máy đọc của đủ 38 cặp (39 excluded / 37 protected) phải cho kết quả
    ĐÚNG qua scope_exclusion_status — excluded trả 'scope_excluded_v1' với đúng
    pair, protected trả None — và CÙNG kết quả với biến thể uppercase và NFD.
    Trả về (list lỗi, n_excluded_members, n_protected_members); lỗi ≠ rỗng →
    compute_status FAIL (exit≠0) — audit không còn PASS chỉ dựa vào nhãn ledger."""
    _, exclusions = load_scope_exclusions()
    errs, n_exc, n_prot = [], 0, 0
    for pair, e in sorted(exclusions.items()):
        exc, prot = _member_sets(e)
        for m in sorted(exc | prot):
            expect_excluded = m in exc
            for v in (m, m.upper(), U.normalize("NFD", m)):
                st = scope_exclusion_status(v)
                got = st["status"] if st else None
                if expect_excluded:
                    if st is None or st.get("pair") != list(pair) \
                            or got != "scope_excluded_v1":
                        errs.append((v, f"subject phải scope_excluded_v1 pair "
                                        f"{list(pair)}, nhận {got}"))
                elif st is not None:
                    errs.append((v, f"protected member bị loại nhầm ({got})"))
            if expect_excluded:
                n_exc += 1
            else:
                n_prot += 1
    return errs, n_exc, n_prot


def scope_policy_hash():
    """Fingerprint policy scope v1 (R14-02, hậu kiểm v14 §4): gắn ledger hiệu lực
    (bytes) + đáp án thành viên pin + source hash của loader/validator/boundary/
    status. Đổi dữ liệu quyết định HOẶC logic tiêu thụ scope → hash ĐỔI; khôi phục
    → về giá trị cũ. Ghi vào report (scope_exclusions_v1.scope_policy_hash) và gộp
    vào domain_config_hash. Probe trước/sau/khôi phục: test_scope_policy.py."""
    import inspect
    return hashlib.sha256(json.dumps({
        "ledger_sha256": hashlib.sha256(
            QD57_EXCLUSIONS.read_bytes()).hexdigest(),
        "expected_members_sha256": hashlib.sha256(
            QD57_EXPECTED_MEMBERS.read_bytes()).hexdigest(),
        "logic_source_sha256": [
            hashlib.sha256(inspect.getsource(f).encode("utf-8")).hexdigest()
            for f in (_member_sets, load_scope_exclusions, scope_exclusion_status,
                      scope_boundary_check)],
    }, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _classifier_snapshot():
    """Snapshot HÀNH THỰC (runtime) của bộ phân lớp + miền sinh (R61-02): bảng
    is_core ĐỌC TỪ MODULE ĐANG CHẠY (mutation in-memory → snapshot đổi) + source
    của các hàm phân lớp (sửa code file → source đổi)."""
    import inspect
    return {
        "classifier_tables": {
            "CORE_ONSET_FIRST": {k: sorted(v)
                                 for k, v in sorted(CORE_ONSET_FIRST.items())},
            "CORE_TAILS": sorted(CORE_TAILS),
        },
        "classifier_source_sha256": [
            hashlib.sha256(inspect.getsource(f).encode("utf-8")).hexdigest()
            for f in (is_core, attest_class, enumerate_syllables, build_groups)
        ],
        "generation_module_sha256": [
            hashlib.sha256((HERE / n).read_bytes()).hexdigest()
            for n in ("vi_rules.py", "vi_syllable.py")
        ],
    }


def domain_config_hash(vocab, prov):
    """Pin HÀNH VI miền audit (reviewer 6.1 điểm 5 + R61-02 + R14-02): inventory_contract_hash
    không đại diện cho hành vi miền mới — hash này gộp bảng pin + builder + ngưỡng +
    các list regression + SNAPSHOT RUNTIME của classifier (bảng is_core đọc từ module
    đang chạy) + hash source các hàm phân lớp + hash module miền sinh + ledger
    scope-exclusion QD57 (bảng quyết định runtime — mutation in-memory hay đổi file
    ledger đều làm hash đổi, nhìn thấy được) + scope_policy_hash (fingerprint logic
    scope — R14-02: sửa load_scope_exclusions/scope_exclusion_status/scope_boundary_
    check cũng làm domain_config_hash đổi)."""
    parts = json.dumps({
        "sha256_vocab": prov["sha256_vocab"],
        "sha256_builder": hashlib.sha256(
            (HERE / "build_core_domain.py").read_bytes()).hexdigest(),
        "attest_min_freq": ATTEST_MIN_FREQ,
        "domain_must_attest": DOMAIN_MUST_ATTEST,
        "domain_must_not": DOMAIN_MUST_NOT,
        "scope_policy_hash": scope_policy_hash(),
        "qd57_scope_exclusions_sha256": hashlib.sha256(
            QD57_EXCLUSIONS.read_bytes()).hexdigest(),
        "behavior": _classifier_snapshot(),
    }, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(parts.encode("utf-8")).hexdigest()


def attest_class(parts4, tone, vocab):
    """(onset, gl, form, tail), tone → 'core' | 'ext' | 'stress'.

    core  = is_core(ngữ cảnh) VÀ chính tả có thanh đó attested trong corpus
            (freq >= ATTEST_MIN_FREQ) — chính tả lõi có căn cứ độc lập.
    ext   = is_core(ngữ cảnh) NHƯNG không attested — miền mở rộng/thử nghiệm:
            giữ trong miền sinh, KHÔNG gate, KHÔNG đòi duyệt đồng âm.
    stress= ngoài ngữ cảnh core (F06) — như trước.
    """
    spelling = U.normalize("NFC", R.render_parts(*parts4, tone)).lower()
    if not is_core(parts4):
        return "stress"
    if vocab.get(spelling, 0) >= ATTEST_MIN_FREQ:
        return "core"
    return "ext"


# Ca reviewer vòng 6 (§5) → REGRESSION của căn cứ miền (không gọi là held-out).
# Phải attested: từ thật của các bộ đối lập + fixture rule; không được attested:
# tổ hợp reviewer nêu là ngoài chính tả lõi + alias nhân tạo (gii).
DOMAIN_MUST_ATTEST = [
    "cây", "mấy", "bêu", "tay", "quay", "lý", "ký", "sĩ", "kỳ", "mỹ", "ích",
    "ưu", "muỗm", "khuỷu", "yếm", "que", "quê", "hue", "huê", "yên",
]
DOMAIN_MUST_NOT = ["câi", "mấi", "bêo", "buâi", "buây", "gii"]


def domain_regression_check(vocab):
    """Trả về list lỗi (rỗng = PASS) trên căn cứ attestation."""
    errs = []
    for w in DOMAIN_MUST_ATTEST:
        sk, ti = R.strip_tone(w)
        p = R.parse_skeleton(sk)
        if p is None:
            errs.append((w, "parse lỗi nhưng phải attested"))
            continue
        tone = R.TONE_BY_INDEX[ti]
        if attest_class(p, tone, vocab) != "core":
            errs.append((w, f"phải core-attested (freq="
                            f"{vocab.get(U.normalize('NFC', w.lower()), 0)})"))
    for w in DOMAIN_MUST_NOT:
        # kiểm CHÍNH TẢ LITERAL: "gii" canonicalize về "gi" (renderer hợp nhất i
        # dùng chung — parts của nó thật sự core) nhưng alias "gii" chính nó phải
        # không attested; tương tự câi/mấi/bêo… phải dưới ngưỡng
        if vocab.get(U.normalize("NFC", w.lower()), 0) >= ATTEST_MIN_FREQ:
            errs.append((w, "không được attested (ngoài chính tả lõi)"))
    return errs


def enumerate_syllables():
    """Sinh theo PARTS (onset, glide, form, tail) — phủ cả vần glide (khuya/khoa/khoe).
    Chỉ nhận combo mà CHÍNH TẢ CANONICAL (render_parts, V5-02 — renderer hợp nhất
    chữ i dùng chung của nhánh gi) parse lại đúng thành combo đó (mỗi chính tả 1
    đường parse, không đếm trùng). Trả list (onset, gl, form, tail, tone, is_core)."""
    out = set()

    def try_parts(parts):
        onset, gl, form, tail = parts
        spelling = R.render_parts(onset, gl, form, tail, "TONE_NGANG")
        if len(spelling) > 7:
            return
        if R.parse_skeleton(spelling) != parts:
            return
        core = is_core(parts)
        tones = (["TONE_SAC", "TONE_NANG"] if R.CODA_MAP[tail] in R._TUC else TONE_IDS)
        for tone in tones:
            out.add((*parts, tone, core))

    for onset in R.ONSETS:
        for form in R.FORMS:
            for tail in R.CODA_MAP:
                try_parts((onset, "", form, tail))
                for gl in ("o", "u"):
                    if gl + form in R.GLIDE_FORMS:
                        try_parts((onset, gl, form, tail))
    return sorted(out)


def id_sequence(parts4, tone_id):
    on, gl, nuc, coda, _ = R.record_parts(*parts4)
    seq = list(on) + list(gl) + [nuc] + ([coda] if coda else [])
    return tuple(seq + [tone_id])


def compute_status(n_unexplained, n_proposal, contrast_fail, core_fail,
                   domain_fail=None, scope_fail=None):
    """MỞ rộng vòng 6.5: scope_fail (lỗi nhất quán ledger↔boundary của scope v1 —
    R14-01) đưa thẳng về FAIL như contrast/core/domain. MỘT status duy nhất từ
    TOÀN BỘ điều kiện lỗi (V5-05 + vòng 6); dùng chung cho JSON/Markdown/stdout/exit."""
    if contrast_fail or n_unexplained or core_fail or domain_fail or scope_fail:
        return "FAIL"
    if n_proposal:
        return "PENDING_APPROVAL"
    return "PASS"


def build_groups(combos, vocab, exclusions=None):
    """Gom nhóm theo chuỗi semantic ID (gồm tone) và phân 3 bucket theo lớp attest:
    gate (≥2 core-attested — đòi giải thích scope), ext (còn ext spelling — miền
    mở rộng/thử nghiệm, KHÔNG gate), stress (còn lại — như vòng 4/5).
    exclusions: ledger QD57 (load_scope_exclusions) — main() LUÔN truyền; gọi trực
    tiếp không truyền = hành vi cũ (không có tier excluded_v1)."""
    groups = {}
    for item in combos:
        parts, tone = item[:4], item[4]
        cls = attest_class(parts, tone, vocab)
        # NFC: place_mark ghép dấu bằng combining mark — spellings trong báo cáo
        # phải chuẩncomposed để khớp bảng attestation và literal trong test
        spelling = U.normalize("NFC", R.render_parts(*parts, tone))
        seq = id_sequence(parts, tone)
        g = groups.setdefault(seq, {"spellings": set(), "parts": [],
                                    "cls": set(), "flags": set()})
        g["spellings"].add(spelling)
        g["parts"].append(parts)
        g["cls"].add((cls, spelling))
        _, _, _, _, flags = R.record_parts(*parts)
        g["flags"] |= flags

    gate_groups, ext_groups, stress_groups = [], [], []
    for seq, g in groups.items():
        skels = sorted({R.strip_tone(s)[0] for s in g["spellings"]})
        if len(skels) < 2:
            continue
        core_spellings = sorted(s for c, s in g["cls"] if c == "core")
        ext_spellings = sorted(s for c, s in g["cls"] if c == "ext")
        entry = {
            "seq": list(seq),
            "spellings": sorted(g["spellings"]),
            "core_spellings": core_spellings,
            "ext_spellings": ext_spellings,
            "skeletons": skels,
            "b_flags": sorted(g["flags"]),
        }
        if len(core_spellings) >= 2:
            # gate = ≥2 chính tả core CÓ CĂN CỨ corpus — nhóm thật sự đòi scope rule
            # vòng 6.3: duyệt hẹp EXACT FIXTURE (reviewer v11 §3) thử TRƯỚC — chỉ
            # đúng cặp đầy đủ dấu (NFC-lower giữ tone) + đúng tone + record khớp
            # expected; KHÔNG dùng flag rộng MR-I-Y (probe v11: flag nâng 52 nhóm).
            core_skels = sorted({R.strip_tone(s)[0] for s in core_spellings})
            group_tone = seq[-1]
            fx_rule = inventory.explain_exact_fixture(core_spellings, group_tone)
            excl = (exclusions or {}).get(tuple(sorted(core_spellings)))
            if fx_rule:
                entry["tier"] = "approved"
                entry["rule"] = fx_rule
                entry["exact_fixture"] = True
            elif excl:
                # QD57-2026-10-02 (chủ dự án chấp thuận): không duyệt merge — giới
                # hạn scope v1 ĐÚNG ĐỐI TƯỢNG (subject), phía protected KHÔNG bị
                # loại. KHÔNG phải approved, KHÔNG phải noise: nhóm gốc + tần suất
                # + trace giữ nguyên trong ledger pin; ranh giới contract (không tự
                # phục hồi dấu/đổi route/ghép tách token) nằm trong ledger và là
                # ràng buộc tiêu thụ fase D.
                tier, rule_id = inventory.explain_collision_tiered(core_skels)
                entry["tier"] = "excluded_v1"
                entry["rule"] = "+".join(rule_id) if rule_id else None
                entry["exact_fixture"] = False
                exc_m, prot_m = _member_sets(excl)
                entry["scope_exclusion"] = {"subject": excl["subject"],
                                            "protected": excl["protected"],
                                            "reason": excl["reason"],
                                            "excluded_members": sorted(exc_m),
                                            "protected_members": sorted(prot_m)}
            else:
                tier, rule_id = inventory.explain_collision_tiered(core_skels)
                entry["tier"] = tier
                entry["rule"] = "+".join(rule_id) if rule_id else None
                entry["exact_fixture"] = False
            # freq từng spelling để reviewer tự đánh giá độ tin cậy thành viên
            # (freq thấp = có thể artifact tách âm tiết/typo — gắn cờ trong scope doc)
            entry["core_freqs"] = {
                s: vocab.get(U.normalize("NFC", s.lower()), 0)
                for s in core_spellings}
            gate_groups.append(entry)
        elif ext_spellings:
            # ≥1 dạng core-ngữ-cảnh nhưng KHÔNG attested (hoặc cặp ext với nhau):
            # tổ hợp thử nghiệm — báo cáo minh bạch, không đòi duyệt merge core
            ext_groups.append(entry)
        else:
            stress_groups.append(entry)
    return gate_groups, ext_groups, stress_groups, len(groups)


def main():
    combos = enumerate_syllables()
    vocab, prov = load_attestation()
    qd57, exclusions = load_scope_exclusions()
    n_core = n_ext = n_stress = 0
    for item in combos:
        cls = attest_class(item[:4], item[4], vocab)
        if cls == "core":
            n_core += 1
        elif cls == "ext":
            n_ext += 1
        else:
            n_stress += 1

    gate_groups, ext_groups, stress_groups, n_id_sequences = \
        build_groups(combos, vocab, exclusions)
    n_unexplained = sum(1 for c in gate_groups if c["tier"] == "unexplained")
    n_proposal = sum(1 for c in gate_groups if c["tier"] == "proposal")
    n_approved = sum(1 for c in gate_groups if c["tier"] == "approved")
    n_identity = sum(1 for c in gate_groups if c["tier"] == "identity")
    n_excluded = sum(1 for c in gate_groups if c["tier"] == "excluded_v1")
    by_rule = {}
    for c in gate_groups:
        key = c["tier"] + ":" + (c["rule"] or "UNEXPLAINED")
        by_rule.setdefault(key, []).append(c["core_spellings"][0])

    # đối chứng bảo toàn đối lập mức chuỗi (tai≠tay, tui≠tuy…)
    contrast_fail, contrast_ok = [], []
    for a, b in inventory.SYLLABLE_LEVEL_CONTRASTS:
        pa = R.parse_skeleton(R.strip_tone(a)[0])
        pb = R.parse_skeleton(R.strip_tone(b)[0])
        if pa is None or pb is None:
            contrast_fail.append((a, b, "parse lỗi"))
            continue
        tone = "TONE_SAC" if {R.CODA_MAP[pa[3]], R.CODA_MAP[pb[3]]} & R._TUC \
            else "TONE_NGANG"
        seq_a, seq_b = id_sequence(pa, tone), id_sequence(pb, tone)
        (contrast_ok if seq_a != seq_b else contrast_fail).append((a, b, None))

    OUT.mkdir(parents=True, exist_ok=True)
    core_fail = core_acceptance_check()
    domain_fail = domain_regression_check(vocab)
    scope_fail, n_scope_exc_m, n_scope_prot_m = scope_boundary_check()
    status = compute_status(n_unexplained, n_proposal, contrast_fail, core_fail,
                            domain_fail, scope_fail)
    # truy vết ĐẦY ĐỦ các nhóm bị đưa ra ngoài gate (reviewer 6.1 điểm 4): không
    # mất dấu collision chưa giải quyết — ext/stress xuất nguyên bản ra jsonl
    for name, groups in (("dieu7_ext_groups.jsonl", ext_groups),
                         ("dieu7_stress_groups.jsonl", stress_groups)):
        with open(OUT / name, "w", encoding="utf-8") as f:
            for g in sorted(groups, key=lambda c: c["spellings"][0]):
                f.write(json.dumps(g, ensure_ascii=False) + "\n")
    report = {
        "audit": "điều 7 — realization-collision (fase B, vòng 6.1: attestation là "
                 "lớp bằng chứng + cách GIỚI HẠN MIỀN ĐÁNH GIÁ — KHÔNG thay xác nhận "
                 "chính tả lõi)",
        "domain_terms": {
            "context_core_candidates": "dạng vượt is_core(ngữ cảnh) — lớp 'core' + "
                                       "'ext' trong code (core_ctx_only)",
            "attested_gate_domain": "context_core_candidates ∩ attestation(freq≥"
                                    f"{ATTEST_MIN_FREQ}) — lớp 'core' trong code; "
                                    "MIỀN GATE duy nhất của report này",
            "extended_or_unattested_domain": "context_core_candidates KHÔNG attested "
                                             "— lớp 'ext' trong code; miền mở rộng, "
                                             "không gate",
            "stress": "ngoài ngữ cảnh core (F06)",
            "trace_files": ["dieu7_ext_groups.jsonl", "dieu7_stress_groups.jsonl"],
        },
        "domain_scope_statement":
            f"Audit trên MIỀN ỨNG VIÊN có chứng thực trong corpus phiên bản "
            f"{prov['sha256_vocab'][:12]}…, ngưỡng tần suất {ATTEST_MIN_FREQ} — "
            "KHÔNG là xác nhận toàn bộ miền chính tả lõi tiếng Việt; thu hẹp gate "
            "không đồng nghĩa giải quyết ngôn ngữ các nhóm ngoài gate (được lưu "
            "dấu đầy đủ trong trace_files).",
        "status": status,
        "n_forms_generated": len(combos),
        "n_forms_core": n_core,
        "n_forms_core_ctx_only": sum(1 for c in combos if c[5]),
        "n_forms_ext": n_ext,
        "n_forms_stress": n_stress,
        "n_id_sequences": n_id_sequences,
        "n_collision_groups_total": len(gate_groups) + len(ext_groups)
                                    + len(stress_groups),
        "n_gate_groups_core": len(gate_groups),
        "n_ext_groups": len(ext_groups),
        "n_gate_approved": n_approved,
        "n_gate_excluded_v1": n_excluded,
        "n_gate_proposal": n_proposal,
        "n_gate_identity": n_identity,
        "n_gate_unexplained": n_unexplained,
        "scope_exclusions_v1": {
            "policy_id": qd57["policy_id"],
            "scope": qd57["scope"],
            "owner_approval": qd57["owner_approval"],
            "source_ledger_sha256": qd57["source_ledger_sha256"],
            "ledger_sha256": hashlib.sha256(
                QD57_EXCLUSIONS.read_bytes()).hexdigest(),
            "expected_members_source": qd57.get("expected_members_source"),
            "scope_policy_hash": scope_policy_hash(),
            "scope_policy_hash_scope": "ledger hiệu lực (bytes) + đáp án thành viên "
                                       "pin (qd57/scope_expected_members_qd57.json) "
                                       "+ source hash _member_sets/load_scope_"
                                       "exclusions/scope_exclusion_status/scope_"
                                       "boundary_check — R14-02",
            "n_excluded_members": n_scope_exc_m,
            "n_protected_members": n_scope_prot_m,
            "boundary_check": {
                "method": "scope_boundary_check: mỗi thành viên máy đọc của 38 cặp "
                          "qua scope_exclusion_status — excluded phải trả trạng thái "
                          "có cấu trúc đúng pair, protected phải trả None; cùng kết "
                          "quả với uppercase/NFD (R14-01)",
                "unicode_variants": ["exact", "UPPER", "NFD"],
                "fail": scope_fail,
            },
            "n_excluded": n_excluded,
            "meaning": "excluded_v1 = KHÔNG duyệt merge, giới hạn bảo đảm đọc v1 "
                       "ĐÚNG ĐỐI TƯỢNG (subject) — phía protected KHÔNG bị loại; "
                       "KHÔNG phải approved, KHÔNG phải tuyên bố noise/sai chính tả",
            "boundary": [
                "không tự phục hồi dấu (nhận xét thue gợi thuế ≠ lệnh thue→thuế)",
                "không tự đổi route — token ngoại không mặc nhiên là EN",
                "không ghép/tách token, không sửa mã hóa, không mở rộng viết tắt",
                "fold/spell chỉ khi contract ủy quyền đúng trường hợp, có "
                "provenance/fallback_reason; out_of_scope_v1 không phải giấy "
                "phép fold/spell mới",
                "khi không có đường xử lý được phép: trả trạng thái không hỗ trợ/"
                "chưa phân giải có cấu trúc, không lặng lẽ phát âm theo record "
                "chưa nhận",
            ],
        },
        "n_stress_only_groups": len(stress_groups),
        "by_rule": {k: len(v) for k, v in sorted(by_rule.items())},
        "n_unapproved_rules": sum(1 for r in inventory.MERGE_RULES
                                  if not r.get("approved")),
        "n_approved_rules": sum(1 for r in inventory.MERGE_RULES
                                if r.get("approved")),
        "withdrawn_rules": [r["rule_id"] for r in inventory.WITHDRAWN_RULES],
        "approval_exact_fixture": {
            "policy": "EXACT_FIXTURE v1 — duyệt ở mức nhóm (vòng 6.3, reviewer "
                      "v11 §3): đúng cặp đầy đủ dấu + đúng tone + record khớp "
                      "expected; approved_scope=core_spellings — alias stress "
                      "trong spellings KHÔNG nằm trong approval",
            "approval_policy_hash": inventory.approval_policy_hash(),
            "n_approved_fixtures": len(inventory.APPROVED_EXACT_FIXTURES),
        },
        "core_domain": {
            "artifact": "02_data/core_domain/vi_syllable_vocab.tsv",
            "sha256_vocab": prov["sha256_vocab"],
            "n_unique_token_forms": prov["n_unique_token_forms"],
            "n_token_occurrences": prov["n_token_occurrences"],
            "unit": prov["unit"],
            "source": prov["corpus_tag"],
            "sha256_corpus": [s["sha256"] for s in prov["source"]],
            "supplement_exclusion": prov["supplement_exclusion"],
            "attest_min_freq": ATTEST_MIN_FREQ,
            "domain_config_hash": domain_config_hash(vocab, prov),
            "domain_config_hash_scope": "sha256_vocab + sha256_builder + "
                                        "attest_min_freq + regression lists + "
                                        "RUNTIME classifier tables (CORE_ONSET_FIRST/"
                                        "CORE_TAILS) + source hash của is_core/"
                                        "attest_class/enumerate_syllables/"
                                        "build_groups + hash module vi_rules.py/"
                                        "vi_syllable.py (miền sinh) + ledger "
                                        "scope-exclusion QD57 "
                                        "(qd57_scope_exclusions.json) + "
                                        "scope_policy_hash (logic scope — R14-02) "
                                        "— R61-02",
            "must_attest": DOMAIN_MUST_ATTEST,
            "must_not": DOMAIN_MUST_NOT,
            "fail": domain_fail,
        },
        "syllable_level_contrasts": {
            "distinct_ok": [a for a, _, _ in contrast_ok],
            "fail": contrast_fail,
        },
        "core_acceptance": {
            "accept": CORE_ACCEPT,
            "reject": CORE_REJECT,
            "fail": core_fail,
        },
        "gate_groups": sorted(gate_groups, key=lambda c: (c["tier"],
                                                          c["core_spellings"][0])),
        "ext_groups": sorted(ext_groups, key=lambda c: c["spellings"][0])[:400],
        "stress_groups": sorted(stress_groups,
                                key=lambda c: c["spellings"][0])[:400],
        "note_core": "attested_gate_domain = is_core(ngữ cảnh, V5-01) ∩ attestation "
                     "corpus tầng 1 (vòng 6.1, min_freq=2) — CÁCH GIỚI HẠN MIỀN ĐÁNH "
                     "GIÁ theo corpus, KHÔNG phải xác nhận chính tả lõi; ext = core-"
                     "ngữ-cảnh nhưng không attested (miền mở rộng, KHÔNG gate KHÔNG "
                     "đòi duyệt đồng âm); stress = ngoài ngữ cảnh core (F06). "
                     "core_acceptance + domain_regression là kiểm độc lập tường minh.",
        "note_B": "b_flags đánh dấu cell [B] (anh/ach, coda nh, qu+ô) — audit không "
                  "chốt âm vị đó; chờ gold/E6 (schema §10)",
        "note_domain": "bảng attestation pin (nguồn corpus tầng 1, sha256 trong "
                       "provenance) là 'dạng token' xuất thô KHÔNG lọc theo parser "
                       "và KHÔNG qua thẩm định chính tả — lỗi gõ/OCR/token lạ có thể "
                       "lặp ≥2 lần, từ hiếm đúng có thể thiếu (bảo thủ — chỉ thu hẹp "
                       "gate). freq<2 coi như typo đơn lẻ, KHÔNG phải quy tắc chính "
                       "tả. Các nhóm ngoài gate lưu dấu đầy đủ trong trace_files; "
                       "tần suất không chứng minh hai dạng cùng phát âm — đồng âm "
                       "vẫn là claim của bảng record, chờ duyệt scope riêng.",
    }
    (OUT / "dieu7_bao_cao.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    md = ["# Điều 7 — realization-collision report (fase B, vòng 6.1)", "",
          f"**Status: {status}**", "",
          f"**Phạm vi:** {report['domain_scope_statement']}", "",
          f"Sinh {len(combos)} dạng (attested {n_core} · ext {n_ext} · "
          f"stress {n_stress}) → "
          f"nhóm GATE (≥2 attested): **{len(gate_groups)}** — approved "
          f"{n_approved} · excluded_v1 {n_excluded} · proposal {n_proposal} · "
          f"identity {n_identity} · unexplained {n_unexplained}",
          f"Nhóm ext (miền mở rộng, không gate — lưu dấu đầy đủ trong "
          f"dieu7_ext_groups.jsonl): {len(ext_groups)} · stress-only (lưu dấu trong "
          f"dieu7_stress_groups.jsonl): {len(stress_groups)}",
          f"Kiểm core độc lập (accept/reject): {len(CORE_ACCEPT)}+{len(CORE_REJECT)}"
          f" từ — {len(core_fail)} lỗi · căn cứ miền (regression attestation): "
          f"{len(DOMAIN_MUST_ATTEST)}+{len(DOMAIN_MUST_NOT)} — {len(domain_fail)} lỗi",
          f"Pin hành vi miền: domain_config_hash "
          f"{report['core_domain']['domain_config_hash']}", "",
          f"Pin policy duyệt exact fixture: approval_policy_hash "
          f"{report['approval_exact_fixture']['approval_policy_hash']} "
          f"({report['approval_exact_fixture']['n_approved_fixtures']} fixture; "
          f"approved_scope=core_spellings)", "",
          f"Pin scope-exclusion QD57-2026-10-02 ({n_excluded} nhóm excluded_v1; "
          f"ledger sha256 {report['scope_exclusions_v1']['ledger_sha256'][:16]}…; "
          f"chủ dự án chấp thuận 02/10 — excluded ≠ approved)", "",
          f"Kiểm ranh giới scope (R14-01): {n_scope_exc_m} excluded + "
          f"{n_scope_prot_m} protected member qua boundary exact NFC+lower giữ dấu "
          f"(exact/UPPER/NFD) — {len(scope_fail)} lỗi · scope_policy_hash "
          f"{report['scope_exclusions_v1']['scope_policy_hash'][:16]}… (R14-02)", ""]
    for rule, examples in sorted(by_rule.items()):
        md.append(f"## {rule} — {len(examples)} nhóm (vd: {', '.join(examples[:4])})")
        md.append("")
    md.append(f"## Đối chứng đối lập (tai≠tay, tui≠tuy…): {len(contrast_ok)} OK, "
              f"{len(contrast_fail)} FAIL")
    (OUT / "dieu7_bao_cao.md").write_text("\n".join(md), encoding="utf-8")

    print(f"SINH: {len(combos)} dạng (attested {n_core} · ext {n_ext} · "
          f"stress {n_stress})")
    print(f"nhóm GATE attested: {len(gate_groups)} — approved {n_approved} · "
          f"excluded_v1 {n_excluded} · proposal {n_proposal} · identity "
          f"{n_identity} · unexplained "
          f"{n_unexplained} · ext không gate {len(ext_groups)} · stress-only "
          f"{len(stress_groups)} (ext/stress lưu dấu đầy đủ trong 02_data/collision/"
          f"dieu7_ext_groups.jsonl / dieu7_stress_groups.jsonl)")
    print("gate theo tier:rule: " + ", ".join(
        f"{k}: {len(v)}" for k, v in sorted(by_rule.items())) or "(trống)")
    print(f"đối chứng SYLLABLE_LEVEL_CONTRASTS: {len(contrast_ok)} phân biệt OK, "
          f"{len(contrast_fail)} FAIL")
    print(f"kiểm core độc lập: {len(CORE_ACCEPT)} accept + {len(CORE_REJECT)} reject, "
          f"{len(core_fail)} lỗi" + (f" {core_fail[:3]}" if core_fail else ""))
    print(f"căn cứ miền attestation (corpus {prov['corpus_tag']}, min_freq="
          f"{ATTEST_MIN_FREQ}): {len(DOMAIN_MUST_ATTEST)} attest + "
          f"{len(DOMAIN_MUST_NOT)} reject, {len(domain_fail)} lỗi"
          + (f" {domain_fail[:3]}" if domain_fail else ""))
    print(f"kiểm ranh giới scope QD57 (R14-01): {n_scope_exc_m} excluded + "
          f"{n_scope_prot_m} protected member, exact/UPPER/NFD, "
          f"{len(scope_fail)} lỗi" + (f" {scope_fail[:3]}" if scope_fail else ""))
    print(f"scope_policy_hash (R14-02): "
          f"{report['scope_exclusions_v1']['scope_policy_hash']}")
    if status == "FAIL":
        reasons = []
        if contrast_fail:
            reasons.append(f"cặp đối lập bị trùng chuỗi {contrast_fail}")
        if n_unexplained:
            reasons.append(f"{n_unexplained} nhóm gate KHÔNG được MERGE_RULES giải thích")
        if core_fail:
            reasons.append(f"core acceptance sai {core_fail[:3]}")
        if domain_fail:
            reasons.append(f"căn cứ miền sai {domain_fail[:3]}")
        if scope_fail:
            reasons.append(f"ranh giới scope sai {scope_fail[:3]}")
        print(f"[7] FAIL — {'; '.join(reasons)}")
        for c in [c for c in gate_groups if c["tier"] == "unexplained"][:20]:
            print(f"    {' · '.join(c['spellings'])}  core={c['core_spellings']}")
    elif status == "PENDING_APPROVAL":
        print("[7] PENDING_APPROVAL — mọi nhóm gate được giải thích nhưng phụ thuộc "
              "rule ĐỀ XUẤT chưa duyệt (0 rule approved ở tầng matcher)")
    else:
        print(f"[7] PASS — scope v1 đã khai: {n_approved} approved + {n_excluded} "
              f"excluded_v1 (QD57-2026-10-02, chủ dự án chấp thuận) + 0 unresolved; "
              f"excluded KHÔNG phải approved — ranh giới contract trong ledger, "
              f"tiêu thụ fase D phải tuân theo")
    return {"FAIL": 1, "PENDING_APPROVAL": 2, "PASS": 0}[status]


if __name__ == "__main__":
    sys.exit(main())
