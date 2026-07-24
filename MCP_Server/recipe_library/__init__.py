"""Recipe Library — reusable musical patterns for Ableton Live.

Provides SQLite-backed storage for chord progressions, drum patterns,
mix templates, and sound design presets. Exposed as MCP tools and resources.
"""
from .database import RecipeDB
from .recipes import get_builtin_recipes

_recipe_db: RecipeDB = None


def get_recipe_db() -> RecipeDB:
    """Get or create the global RecipeDB instance."""
    global _recipe_db
    if _recipe_db is None:
        _recipe_db = RecipeDB()
        _recipe_db.init_db(builtin_recipes=get_builtin_recipes())
    return _recipe_db


def register_recipe_tools(mcp, get_ableton_connection):
    """Register recipe library MCP tools and resources."""
    from . import tools as _tools
    from . import resources as _resources
    _tools.register(mcp, get_ableton_connection, get_recipe_db)
    _resources.register(mcp, get_recipe_db)
