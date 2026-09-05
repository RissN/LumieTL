"""Unit tests for SQLite history manager."""

from core.history_manager import HistoryEntry, HistoryManager


def test_history_crud(tmp_path):
    db_file = tmp_path / "test_history.db"
    hm = HistoryManager(db_file)

    assert hm.count() == 0

    entry1 = HistoryEntry(
        input_path="/path/to/img1.png",
        output_path="/path/to/out1.png",
        source_lang="JPN",
        target_lang="ID",
        engine="google",
        duration=1.85,
        success=True,
    )
    id1 = hm.add(entry1)
    assert id1 is not None
    assert hm.count() == 1

    entry2 = HistoryEntry(
        input_path="/path/to/img2.png",
        output_path=None,
        source_lang="KOR",
        target_lang="ID",
        engine="deepl",
        duration=0.5,
        success=False,
        error="Rate limit exceeded",
    )
    id2 = hm.add(entry2)
    assert id2 is not None
    assert hm.count() == 2

    # Filter checks
    successful_entries = hm.get_all(success=True)
    assert len(successful_entries) == 1
    assert successful_entries[0].engine == "google"

    deepl_entries = hm.get_all(engine="deepl")
    assert len(deepl_entries) == 1
    assert deepl_entries[0].success is False

    # Delete entry
    hm.delete(id1)
    assert hm.count() == 1

    # Clear all
    hm.clear_all()
    assert hm.count() == 0
