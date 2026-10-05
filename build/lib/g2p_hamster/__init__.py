"""g2p-hamster — Front-end TTS Việt/Anh: text thô → phôn vị.

Import chính:
    from g2p_hamster import text_to_profile_v2_full   # bản v2 đầy đủ
    from g2p_hamster import text_to_profile_v2        # API cũ (p, errs, notes)
    from g2p_hamster import text_to_profile           # v1 fail-closed

Lõi thuần stdlib; espeak-ng binary là tuỳ chọn (nguồn cứu phiên âm anh).
"""
__version__ = "0.2.0"

__all__ = ["text_to_profile", "text_to_profile_v2", "text_to_profile_v2_full",
           "v2_provenance", "v2_policy_hash", "__version__"]


def __getattr__(name):
    # nạp lười: import g2p_hamster thì chưa tải từ điển; gọi hàm mới tải
    if name in __all__:
        if name == "text_to_profile":
            from .g2p_v1 import text_to_profile
            return text_to_profile
        from .g2p_v2 import (v2_policy_hash, v2_provenance,
                             text_to_profile_v2, text_to_profile_v2_full)
        return {"text_to_profile_v2": text_to_profile_v2,
                "text_to_profile_v2_full": text_to_profile_v2_full,
                "v2_policy_hash": v2_policy_hash,
                "v2_provenance": v2_provenance}[name]
    raise AttributeError(f"module 'g2p_hamster' không có thuộc tính {name!r}")
