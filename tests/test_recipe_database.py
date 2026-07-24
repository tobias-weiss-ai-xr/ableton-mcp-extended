"""Tests for RecipeDB — SQLite CRUD and search."""
import pytest
import json
import os
from MCP_Server.recipe_library.database import RecipeDB


SEED_DATA = [{"category": "chord_progression", "name": "Seed Prog", "tags": "", "description": "", "data": "{}"}]


@pytest.fixture
def db():
    """Create in-memory RecipeDB for each test."""
    database = RecipeDB(":memory:")
    database.init_db(builtin_recipes=SEED_DATA)
    return database


class TestRecipeDBCRUD:
    def test_create_and_get(self, db):
        recipe_id = db.create(
            category="chord_progression",
            name="Test Progression",
            data=json.dumps({"key": "C", "scale": "major", "chords": ["C", "F", "G"], "voicing": "open", "mood": "happy"}),
            tags="pop,happy",
            description="A test progression"
        )
        recipe = db.get(recipe_id)
        assert recipe is not None
        assert recipe["name"] == "Test Progression"
        assert recipe["category"] == "chord_progression"
        assert recipe["is_builtin"] == 0

    def test_get_not_found(self, db):
        result = db.get(999)
        assert result is None

    def test_update(self, db):
        recipe_id = db.create("chord_progression", "Test", "{}", "tag", "desc")
        db.update(recipe_id, name="Updated Name")
        recipe = db.get(recipe_id)
        assert recipe["name"] == "Updated Name"

    def test_update_builtin_raises(self, db):
        db.seed_builtin([
            {"category": "chord_progression", "name": "Builtin", "tags": "", "description": "", "data": "{}"}
        ])
        builtins = db.search(category="chord_progression")
        builtin_id = builtins[0]["id"]
        with pytest.raises(ValueError, match="Cannot update built-in"):
            db.update(builtin_id, name="New Name")

    def test_delete(self, db):
        recipe_id = db.create("chord_progression", "To Delete", "{}", "", "")
        db.delete(recipe_id)
        assert db.get(recipe_id) is None

    def test_delete_builtin_raises(self, db):
        db.seed_builtin([
            {"category": "chord_progression", "name": "BuiltinDel", "tags": "", "description": "", "data": "{}"}
        ])
        builtins = db.search(category="chord_progression")
        builtin_id = builtins[0]["id"]
        with pytest.raises(ValueError, match="Cannot delete built-in"):
            db.delete(builtin_id)


class TestRecipeDBSearch:
    def test_search_by_category(self, db):
        db.create("chord_progression", "CP1", "{}", "", "")
        db.create("drum_pattern", "DP1", "{}", "", "")
        results = db.search(category="chord_progression")
        assert any(r["name"] == "CP1" for r in results)
        assert all(r["category"] == "chord_progression" for r in results)

    def test_search_by_tags(self, db):
        db.create("chord_progression", "A", "{}", "pop,upbeat", "")
        db.create("chord_progression", "B", "{}", "jazz,chill", "")
        results = db.search(tags="pop")
        assert len(results) == 1
        assert results[0]["name"] == "A"

    def test_search_and_tags(self, db):
        db.create("chord_progression", "X", "{}", "pop,jazz", "")
        results = db.search(tags="pop,jazz")
        assert len(results) == 1

    def test_search_by_query(self, db):
        db.create("chord_progression", "Sunshine Pop", "{}", "", "Upbeat major progression")
        results = db.search(query="sunshine")
        assert len(results) == 1

    def test_search_all(self, db):
        db.create("chord_progression", "A", "{}", "", "")
        db.create("drum_pattern", "B", "{}", "", "")
        results = db.search()
        assert len(results) >= 2

    def test_search_empty(self, db):
        db2 = RecipeDB(":memory:")
        db2.init_db(builtin_recipes=[])
        results = db2.search()
        assert len(results) == 0


class TestRecipeDBSeeding:
    def test_seed_on_init(self, db):
        count = db.get_builtin_count()
        assert count > 0

    def test_seed_idempotent(self, db):
        db.seed_builtin([
            {"category": "chord_progression", "name": "Builtin", "tags": "", "description": "", "data": "{}"}
        ])
        count1 = db.get_builtin_count()
        db.seed_builtin([
            {"category": "chord_progression", "name": "Builtin", "tags": "", "description": "", "data": "{}"}
        ])
        count2 = db.get_builtin_count()
        assert count1 == count2

    def test_create_and_get_builtin(self, db):
        db.seed_builtin([
            {"category": "drum_pattern", "name": "Test Builtin", "tags": "", "description": "", "data": "{}"}
        ])
        results = db.search(category="drum_pattern")
        assert len(results) == 1
        assert results[0]["name"] == "Test Builtin"
        assert results[0]["is_builtin"] == 1

    def test_get_builtin_count_empty(self):
        db = RecipeDB(":memory:")
        db.init_db(builtin_recipes=[])
        assert db.get_builtin_count() == 0
