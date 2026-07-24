"""Tests for recipe library MCP tools and resources."""
import pytest
import json
from unittest.mock import Mock, patch
from MCP_Server.recipe_library.database import RecipeDB


@pytest.fixture
def db():
    database = RecipeDB(":memory:")
    SEED = [{"category": "chord_progression", "name": "Seed", "tags": "", "description": "", "data": "{}"}]
    database.init_db(builtin_recipes=SEED)
    return database


@pytest.fixture
def mock_get_db(db):
    def _get_db():
        return db
    return _get_db


class TestListRecipes:
    def test_list_all(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_list_recipes
        result = json.loads(_impl_list_recipes(mock_get_db))
        assert result["status"] == "success"
        assert "count" in result
        assert "recipes" in result

    def test_list_by_category(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_list_recipes
        result = json.loads(_impl_list_recipes(mock_get_db, category="chord_progression"))
        assert result["status"] == "success"
        for r in result["recipes"]:
            assert r["category"] == "chord_progression"

    def test_list_by_tags(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_list_recipes
        db = mock_get_db()
        db.create("chord_progression", "Tagged", "{}", "pop,test", "desc")
        result = json.loads(_impl_list_recipes(mock_get_db, tags="test"))
        assert result["status"] == "success"
        assert any(r["name"] == "Tagged" for r in result["recipes"])

    def test_list_by_query(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_list_recipes
        result = json.loads(_impl_list_recipes(mock_get_db, query="Seed"))
        assert result["status"] == "success"

    def test_list_empty_result(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_list_recipes
        result = json.loads(_impl_list_recipes(mock_get_db, query="zzz_nonexistent"))
        assert result["status"] == "success"
        assert len(result["recipes"]) == 0


class TestGetRecipe:
    def test_get_existing(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_get_recipe
        db = mock_get_db()
        rid = db.create("chord_progression", "GetTest", '{"key":"C"}', "tag", "desc")
        result = json.loads(_impl_get_recipe(mock_get_db, rid))
        assert result["status"] == "success"
        assert result["recipe"]["name"] == "GetTest"

    def test_get_not_found(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_get_recipe
        result = json.loads(_impl_get_recipe(mock_get_db, 999))
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


class TestCreateRecipe:
    def test_create_valid(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_create_recipe
        result = json.loads(_impl_create_recipe(
            mock_get_db, "chord_progression", "NewProg",
            '{"key":"C","scale":"major","chords":["C"],"voicing":"open","mood":"test"}',
            "test", "Test progression"
        ))
        assert result["status"] == "success"
        assert "id" in result

    def test_create_invalid_data(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_create_recipe
        result = json.loads(_impl_create_recipe(
            mock_get_db, "chord_progression", "Bad",
            '{"invalid": true}', "", ""
        ))
        assert result["status"] == "error"

    def test_create_invalid_json(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_create_recipe
        result = json.loads(_impl_create_recipe(
            mock_get_db, "chord_progression", "Bad", "not json", "", ""
        ))
        assert result["status"] == "error"


class TestUpdateRecipe:
    def test_update_valid(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_update_recipe
        db = mock_get_db()
        rid = db.create("chord_progression", "OldName", "{}", "", "")
        result = json.loads(_impl_update_recipe(mock_get_db, rid, name="NewName"))
        assert result["status"] == "success"
        assert db.get(rid)["name"] == "NewName"

    def test_update_builtin(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_update_recipe
        result = json.loads(_impl_update_recipe(mock_get_db, 1, name="Hack"))
        assert result["status"] == "error"
        assert "built-in" in result["message"].lower()


class TestDeleteRecipe:
    def test_delete_valid(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_delete_recipe
        db = mock_get_db()
        rid = db.create("chord_progression", "DelMe", "{}", "", "")
        result = json.loads(_impl_delete_recipe(mock_get_db, rid))
        assert result["status"] == "success"

    def test_delete_builtin(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_delete_recipe
        result = json.loads(_impl_delete_recipe(mock_get_db, 1))
        assert result["status"] == "error"
        assert "built-in" in result["message"].lower()

    def test_delete_not_found(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_delete_recipe
        result = json.loads(_impl_delete_recipe(mock_get_db, 999))
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


class TestSeedRecipes:
    def test_seed(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_seed_recipes
        result = json.loads(_impl_seed_recipes(mock_get_db))
        assert result["status"] == "success"
        assert result["count"] >= 0


class TestApplyRecipe:
    def test_apply_not_found(self, mock_get_db):
        from MCP_Server.recipe_library.tools import _impl_apply_recipe
        result = json.loads(_impl_apply_recipe(mock_get_db, 999, None))
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


class TestResources:
    def test_resource_list_categories(self, mock_get_db):
        from MCP_Server.recipe_library.resources import _impl_list_categories
        result = _impl_list_categories(mock_get_db)
        assert result is not None
        data = json.loads(result)
        assert "categories" in data

    def test_resource_list_category(self, mock_get_db):
        from MCP_Server.recipe_library.resources import _impl_list_category
        result = _impl_list_category(mock_get_db, "chord_progression")
        data = json.loads(result)
        assert "recipes" in data
        assert data["category"] == "chord_progression"

    def test_resource_get_recipe(self, mock_get_db):
        from MCP_Server.recipe_library.resources import _impl_get_recipe_resource
        db = mock_get_db()
        rid = db.create("drum_pattern", "ResTest", "{}", "", "")
        result = _impl_get_recipe_resource(mock_get_db, rid)
        data = json.loads(result)
        assert data["id"] == rid

    def test_resource_get_not_found(self, mock_get_db):
        from MCP_Server.recipe_library.resources import _impl_get_recipe_resource
        result = _impl_get_recipe_resource(mock_get_db, 999)
        assert result is None
