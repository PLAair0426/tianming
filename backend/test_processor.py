import pytest

from app.core import processor


def base_result():
    return {
        "original_hexagram": [7, 7, 7, 7, 7, 7],
        "changed_hexagram": [7, 7, 7, 7, 7, 7],
        "original_binary": [1, 1, 1, 1, 1, 1],
        "changed_binary": [1, 1, 1, 1, 1, 1],
    }


def fake_get_hexagram_info(upper_bin, lower_bin):
    joined = "".join(str(bit) for bit in [*lower_bin, *upper_bin])
    return f"卦{joined}", "☰\n☰", "天\n天"


def test_output_hexagram_results_corrects_original_hexagram_mismatch(monkeypatch):
    input_values = [6, 7, 8, 9, 6, 7]
    result = base_result()
    result["original_hexagram"] = [7, 7, 7, 7, 7, 7]

    monkeypatch.setattr(processor, "get_hexagram_result", lambda values: result)
    monkeypatch.setattr(processor, "get_hexagram_info", fake_get_hexagram_info)
    monkeypatch.setattr(
        processor,
        "validate_hexagram_data",
        lambda data: {"valid": True, "errors": [], "warnings": [], "fixed": None},
    )

    hexagram_data = processor.output_hexagram_results(input_values)

    assert hexagram_data["original_hexagram"] == input_values
    assert hexagram_data["original_binary"] == [0, 1, 0, 1, 0, 1]


def test_output_hexagram_results_uses_fixed_validation_data(monkeypatch):
    monkeypatch.setattr(processor, "get_hexagram_result", lambda values: base_result())
    monkeypatch.setattr(processor, "get_hexagram_info", fake_get_hexagram_info)
    monkeypatch.setattr(
        processor,
        "validate_hexagram_data",
        lambda data: {
            "valid": False,
            "errors": ["名称需要修复"],
            "warnings": ["已自动修复"],
            "fixed": {"original_name": "修复后卦名"},
        },
    )

    hexagram_data = processor.output_hexagram_results([7, 7, 7, 7, 7, 7])

    assert hexagram_data["original_name"] == "修复后卦名"


def test_output_hexagram_results_raises_on_unrecoverable_validation_error(monkeypatch):
    monkeypatch.setattr(processor, "get_hexagram_result", lambda values: base_result())
    monkeypatch.setattr(processor, "get_hexagram_info", fake_get_hexagram_info)
    monkeypatch.setattr(
        processor,
        "validate_hexagram_data",
        lambda data: {"valid": False, "errors": ["不可修复"], "warnings": [], "fixed": None},
    )

    with pytest.raises(ValueError, match="不可修复"):
        processor.output_hexagram_results([7, 7, 7, 7, 7, 7])
