"""g2p-hamster — Front-end TTS Việt/Anh: text thô → phôn vị.

Import chính:
    from g2p_hamster import text_to_profile_v2_full   # bản v2 đầy đủ
    from g2p_hamster import text_to_profile_v2        # API cũ (p, errs, notes)
    from g2p_hamster import text_to_profile           # v1 fail-closed

Lõi thuần stdlib; espeak-ng binary là tuỳ chọn (nguồn cứu phiên âm anh).
"""
try:
    # không hardcode — đồng bộ với pyproject/wheel (0.2.2 phát hành với
    # attr "0.2.1" do quên bump chỗ này)
    from importlib.metadata import version as _v
    __version__ = _v("g2p-hamster")
except Exception:
    __version__ = "0.2.7"

__all__ = ["text_to_profile", "text_to_profile_v1", "text_to_profile_v2",
           "text_to_profile_v2_full", "v2_provenance", "v2_policy_hash",
           "__version__"]


def __getattr__(name):
    # nạp lười: import g2p_hamster thì chưa tải từ điển; gọi hàm mới tải.
    # 0.2.6: text_to_profile là V2 (khuyên dùng) — chấm dứt footgun mà
    # cả hai đợt đánh giá độc lập đều bắt: tên "mặc định" trỏ vào bản v1
    # fail-closed rụng email/SĐT. Bản v1 đổi tên tường minh
    # text_to_profile_v1 (chưa ai dùng package nên đổi không vỡ ai).
    if name in __all__:
        if name == "text_to_profile_v1":
            from .g2p_v1 import text_to_profile as _v1
            return _v1
        from .g2p_v2 import (v2_policy_hash, v2_provenance,
                             text_to_profile_v2, text_to_profile_v2_full)
        return {"text_to_profile": text_to_profile_v2,
                "text_to_profile_v2": text_to_profile_v2,
                "text_to_profile_v2_full": text_to_profile_v2_full,
                "v2_policy_hash": v2_policy_hash,
                "v2_provenance": v2_provenance}[name]
    raise AttributeError(f"module 'g2p_hamster' không có thuộc tính {name!r}")
