"""MCP tool implementations for the recipe library."""
import json
import logging
from typing import Optional
from .database import RecipeDB

logger = logging.getLogger("AbletonMCPServer")


def register(mcp, get_ableton_connection, get_recipe_db):
    """Register recipe library MCP tools."""

    @mcp.tool()
    def list_recipes(
        ctx, category: Optional[str] = None,
        tags: Optional[str] = None, query: Optional[str] = None
    ) -> str:
        """List recipes, optionally filtered by category, tags, or text query.

        Parameters:
        - category: Filter by category (chord_progression, drum_pattern, mix_template, sound_design)
        - tags: Filter by comma-separated tags (AND match)
        - query: Text search in name and description
        """
        return _impl_list_recipes(get_recipe_db, category, tags, query)

    @mcp.tool()
    def get_recipe(ctx, recipe_id: int) -> str:
        """Get a single recipe by ID with full data.

        Parameters:
        - recipe_id: The recipe ID
        """
        return _impl_get_recipe(get_recipe_db, recipe_id)

    @mcp.tool()
    def create_recipe(
        ctx, category: str, name: str, data: str,
        tags: str = "", description: str = ""
    ) -> str:
        """Create a new user recipe.

        Parameters:
        - category: Recipe category
        - name: Recipe name
        - data: JSON string with category-specific fields
        - tags: Comma-separated tags
        - description: Short description
        """
        return _impl_create_recipe(get_recipe_db, category, name, data, tags, description)

    @mcp.tool()
    def update_recipe(
        ctx, recipe_id: int,
        name: Optional[str] = None, data: Optional[str] = None,
        tags: Optional[str] = None, description: Optional[str] = None
    ) -> str:
        """Update a user recipe's fields. Cannot update built-in recipes.

        Parameters:
        - recipe_id: The recipe ID to update
        - name: New name (optional)
        - data: New data JSON (optional)
        - tags: New tags (optional)
        - description: New description (optional)
        """
        return _impl_update_recipe(get_recipe_db, recipe_id, name, data, tags, description)

    @mcp.tool()
    def delete_recipe(ctx, recipe_id: int) -> str:
        """Delete a user recipe by ID. Cannot delete built-in recipes.

        Parameters:
        - recipe_id: The recipe ID to delete
        """
        return _impl_delete_recipe(get_recipe_db, recipe_id)

    @mcp.tool()
    def apply_recipe(
        ctx, recipe_id: int, track_index: Optional[int] = None
    ) -> str:
        """Apply a recipe to the Ableton session.

        For chord_progressions: returns chord data to create a MIDI clip.
        For drum_patterns: returns pattern data to create a drum clip.
        For mix_templates: returns template config data (use with agentic_mix).
        For sound_design: returns device parameters to apply.

        Parameters:
        - recipe_id: Recipe ID to apply
        - track_index: Target track index (optional, needed for clip/devices)
        """
        return _impl_apply_recipe(get_recipe_db, recipe_id, track_index)

    @mcp.tool()
    def seed_recipes(ctx) -> str:
        """Re-seed all built-in recipes. Idempotent."""
        return _impl_seed_recipes(get_recipe_db)


def _impl_list_recipes(get_db, category=None, tags=None, query=None):
    try:
        db = get_db()
        recipes = db.search(category=category, tags=tags, query=query)
        return json.dumps({"status": "success", "count": len(recipes), "recipes": recipes}, indent=2)
    except Exception as e:
        logger.error(f"Error listing recipes: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_get_recipe(get_db, recipe_id):
    try:
        db = get_db()
        recipe = db.get(recipe_id)
        if recipe is None:
            return json.dumps({"status": "error", "message": f"Recipe {recipe_id} not found"})
        recipe["data"] = json.loads(recipe["data"])
        return json.dumps({"status": "success", "recipe": recipe}, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error getting recipe {recipe_id}: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_create_recipe(get_db, category, name, data, tags, description):
    try:
        from .models import validate_category_data
        validate_category_data(category, data)
        db = get_db()
        recipe_id = db.create(category=category, name=name, data=data, tags=tags, description=description)
        return json.dumps({"status": "success", "id": recipe_id})
    except ValueError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        logger.error(f"Error creating recipe: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_update_recipe(get_db, recipe_id, name=None, data=None, tags=None, description=None):
    try:
        db = get_db()
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if data is not None:
            kwargs["data"] = data
        if tags is not None:
            kwargs["tags"] = tags
        if description is not None:
            kwargs["description"] = description
        db.update(recipe_id, **kwargs)
        return json.dumps({"status": "success", "id": recipe_id})
    except ValueError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        logger.error(f"Error updating recipe {recipe_id}: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_delete_recipe(get_db, recipe_id):
    try:
        db = get_db()
        db.delete(recipe_id)
        return json.dumps({"status": "success"})
    except ValueError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        logger.error(f"Error deleting recipe {recipe_id}: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_seed_recipes(get_db):
    try:
        from .recipes import get_builtin_recipes
        db = get_db()
        recipes = get_builtin_recipes()
        db.seed_builtin(recipes)
        return json.dumps({"status": "success", "count": len(recipes)})
    except Exception as e:
        logger.error(f"Error seeding recipes: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def _impl_apply_recipe(get_db, recipe_id, track_index):
    try:
        db = get_db()
        recipe = db.get(recipe_id)
        if recipe is None:
            return json.dumps({"status": "error", "message": f"Recipe {recipe_id} not found"})
        data = json.loads(recipe["data"])
        category = recipe["category"]
        if category == "mix_template":
            return json.dumps({"status": "success", "applied": False,
                               "message": "Mix templates are applied via agentic_mix. Use the data as Config.",
                               "template": data}, indent=2)
        if track_index is None:
            return json.dumps({"status": "error",
                               "message": f"track_index is required for {category} recipes"})
        if category == "chord_progression":
            return json.dumps({"status": "success", "applied": False,
                               "message": "Use create_clip + add_notes_to_clip with these chords",
                               "chords": data["chords"], "key": data["key"], "track_index": track_index}, indent=2)
        if category == "drum_pattern":
            return json.dumps({"status": "success", "applied": False,
                               "message": "Use create_drum_pattern with these parameters",
                               "pattern_type": data["pattern_type"], "kit_query": data["kit_query"],
                               "bars": data["bars"], "grid": data.get("grid", ""),
                               "track_index": track_index}, indent=2)
        if category == "sound_design":
            return json.dumps({"status": "success", "applied": False,
                               "message": "Load the device, then use set_device_parameter for each parameter",
                               "device_type": data["device_type"], "parameters": data["parameters"],
                               "track_index": track_index}, indent=2)
        return json.dumps({"status": "error", "message": f"Unknown category: {category}"})
    except Exception as e:
        logger.error(f"Error applying recipe {recipe_id}: {e}")
        return json.dumps({"status": "error", "message": str(e)})
