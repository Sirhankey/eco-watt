import json

from scripts.import_catalogs import build_import_payloads


def read_json(name):
    with open(f"ecowatt/data/{name}", encoding="utf-8") as source:
        return json.load(source)


def test_seed_preserves_all_existing_json_records_and_payloads():
    payloads = build_import_payloads()
    appliances = read_json("appliances.json")
    components = read_json("pc_components.json")
    facts = read_json("facts.json")
    presets = read_json("presets.json")

    assert len(payloads["official_appliances"]) == len(appliances)
    assert len(payloads["official_pc_components"]) == sum(len(items) for items in components.values())
    assert len(payloads["official_facts"]) == len(facts)
    assert len(payloads["official_presets"]) == len(presets)
    assert len(payloads["official_preset_items"]) == sum(len(p["appliances"]) for p in presets)

    assert all(record["name"] == source["name"] for record, source in zip(payloads["official_appliances"], appliances))
    assert all(record["body"] == source["fact"] for record, source in zip(payloads["official_facts"], facts))
    assert all(record["description"] == source.get("description") for record, source in zip(payloads["official_presets"], presets))
    assert all(item["snapshot"] == source_item for preset in presets for item, source_item in zip(
        [record for record in payloads["official_preset_items"] if record["preset_id"] == preset["id"]],
        preset["appliances"],
    ))


def test_seed_adds_disabled_quiz_and_questions_with_stable_ids():
    payloads = build_import_payloads()
    quizzes = payloads["event_quizzes"]
    questions = payloads["quiz_questions"]

    assert len(quizzes) == 1
    assert quizzes[0]["enabled"] is False
    assert len(questions) == 3
    assert {question["quiz_id"] for question in questions} == {quizzes[0]["id"]}
    assert len({question["id"] for question in questions}) == 3
    assert all(len(question["options"]) > question["correct_option"] for question in questions)
