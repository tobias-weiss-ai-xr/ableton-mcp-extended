"""MCP resource handlers for the recipe library."""
import json
from .database import RecipeDB


def register(mcp, get_recipe_db):
    """Register recipe library MCP resources."""

    @mcp.resource("live://recipes/")
    def all_categories() -> str:
        """List all recipe categories with counts."""
        return _impl_list_categories(get_recipe_db)

    @mcp.resource("live://recipes/{category}")
    def category_listing(category: str) -> str:
        """List recipes in a category."""
        return _impl_list_category(get_recipe_db, category)

    @mcp.resource("live://recipes/{category}/{recipe_id}")
    def recipe_detail(category: str, recipe_id: int) -> str:
        """Get full recipe detail."""
        return _impl_get_recipe_resource(get_recipe_db, recipe_id) or ""


def _impl_list_categories(get_db):
    try:
        db = get_db()
        categories = ["chord_progression", "drum_pattern", "mix_template", "sound_design"]
        result = {"categories": []}
        for cat in categories:
            recipes = db.search(category=cat)
            result["categories"].append({"category": cat, "count": len(recipes),
                                          "name": cat.replace("_", " ").title()})
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _impl_list_category(get_db, category):
    try:
        db = get_db()
        recipes = db.search(category=category)
        return json.dumps({"category": category, "count": len(recipes), "recipes": recipes},
                          indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _impl_get_recipe_resource(get_db, recipe_id):
    try:
        db = get_db()
        recipe = db.get(recipe_id)
        if recipe is None:
            return None
        recipe["data"] = json.loads(recipe["data"])
        return json.dumps(recipe, indent=2, default=str)
    except Exception:
        return None
