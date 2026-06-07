import json

from agent.tools import file_loader


def test_loader_node_loads_existing_files_and_skips_missing(monkeypatch, tmp_path, make_state):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "concept-a.md").write_text("# Concept A\nContent for A")

    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({"concepts": [
        {"id": "concept-a", "file": "concept-a.md"},
        {"id": "concept-b", "file": "concept-b.md"},
    ]}))

    monkeypatch.setattr(file_loader, "WIKI_PATH", str(wiki_dir))
    monkeypatch.setattr(file_loader, "INDEX_PATH", str(index_path))

    state = make_state(selected_concepts=["concept-a", "concept-b"])

    result = file_loader.loader_node(state)

    assert result["loaded_content"]["concept-a"] == "# Concept A\nContent for A"
    assert result["loaded_content"]["concept-b"] == ""
    assert result["status"] == "planning"


def test_loader_node_falls_back_to_id_md_when_not_in_index(monkeypatch, tmp_path, make_state):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "concept-c.md").write_text("Concept C content")

    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({"concepts": []}))

    monkeypatch.setattr(file_loader, "WIKI_PATH", str(wiki_dir))
    monkeypatch.setattr(file_loader, "INDEX_PATH", str(index_path))

    state = make_state(selected_concepts=["concept-c"])

    result = file_loader.loader_node(state)

    assert result["loaded_content"]["concept-c"] == "Concept C content"
