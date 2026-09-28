from ecowatt.services import catalog_repository


def test_official_loaders_keep_local_fallback_contract():
    appliances = catalog_repository.load_official_appliances()
    components = catalog_repository.load_official_pc_components()
    facts = catalog_repository.load_official_facts()
    presets = catalog_repository.load_official_presets()

    assert appliances
    assert "cpus" in components
    assert facts
    assert presets


def test_official_appliance_loader_marks_supabase_source(monkeypatch):
    monkeypatch.setattr(catalog_repository, "is_supabase_configured", lambda: True)
    monkeypatch.setattr(
        catalog_repository,
        "_fetch_table",
        lambda table, filters=None: [{
            "id": "remote-lamp",
            "name": "Lampada remota",
            "power_watts": 9,
            "default_hours_per_day": 4,
            "default_days_per_month": 30,
            "category": "Sala",
        }],
    )

    appliances = catalog_repository.load_official_appliances()

    assert appliances[0].id == "remote-lamp"
    assert catalog_repository.st.session_state.catalog_source == "Supabase"


def test_official_preset_loader_rebuilds_nested_items_from_supabase(monkeypatch):
    monkeypatch.setattr(catalog_repository, "is_supabase_configured", lambda: True)

    def fetch(table, filters=None):
        if table == "official_presets":
            return [{"id": "preset-1", "name": "Casa remota"}]
        if table == "official_preset_items":
            return [{
                "id": "item-1",
                "preset_id": "preset-1",
                "name": "Lampada remota",
                "category": "Sala",
                "power_watts": 9,
                "hours_per_day": 4,
                "days_per_month": 30,
            }]
        raise AssertionError(table)

    monkeypatch.setattr(catalog_repository, "_fetch_table", fetch)

    presets = catalog_repository.load_official_presets()

    assert presets[0]["appliances"][0]["id"] == "item-1"
    assert catalog_repository.st.session_state.catalog_source == "Supabase"


def test_remote_pc_loader_maps_display_categories_to_builder_keys(monkeypatch):
    monkeypatch.setattr(catalog_repository, "is_supabase_configured", lambda: True)
    monkeypatch.setattr(catalog_repository, "feature_enabled", lambda name, default=False: True)
    categories = ["CPU", "GPU", "Motherboard", "RAM", "Storage", "Monitor", "Peripherals"]
    monkeypatch.setattr(
        catalog_repository,
        "_fetch_table",
        lambda table, filters=None: [
            {
                "id": category.lower(),
                "name": category,
                "category": category,
                "tdp_watts": 10,
                "idle_watts": 1,
                "typical_load_watts": 5,
                "gaming_load_watts": 8,
            }
            for category in categories
        ],
    )

    catalog = catalog_repository.load_official_pc_components()

    assert set(catalog) == {"cpus", "gpus", "motherboards", "rams", "storages", "monitors", "peripherals"}
