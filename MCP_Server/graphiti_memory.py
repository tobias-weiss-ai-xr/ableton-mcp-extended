# Optional Graphiti MCP Memory Backend
#
# Provides persistent, temporally-aware knowledge graph memory for the
# MemorySystem in music_generation.py. When Graphiti MCP server is running,
# this backend stores/retrieves generation patterns as graph episodes
# with auto-extracted entities. When not available, gracefully degrades.
#
# Usage:
#     from MCP_Server.graphiti_memory import GraphitiMemoryBackend
#     backend = GraphitiMemoryBackend()
#     if backend.enabled:
#         backend.record_success(...)
#
# Dependencies:
# - Graphiti MCP server (optional): https://github.com/getzep/graphiti
# - httpx (optional, only if using Graphiti)

import json
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Try importing httpx for Graphiti HTTP transport — optional dependency
try:
    import httpx

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


class GraphitiMemoryBackend:
    """
    Optional persistent backend for MemorySystem powered by Graphiti MCP.
    
    Connects to Graphiti MCP server (separate process) via HTTP transport.
    If Graphiti is not running, all operations silently fall back to no-ops
    and `enabled` returns False.
    
    Pattern entities extracted:
    - genre (e.g., "dub_techno")
    - key (e.g., "Fm")
    - tempo (BPM)
    - instrument_type (e.g., "bass", "kick")
    - density (notes per bar)
    - quality (user rating 1-10)
    
    Usage:
        backend = GraphitiMemoryBackend(
            endpoint="http://localhost:8083/mcp/",
            group_id="ableton-dub-techno"
        )
        if backend.enabled:
            backend.record_success("dub_techno", {"key": "Fm", "tempo": 126}, 8)
            recommendation = backend.recommend("dub_techno")
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        group_id: str = "ableton-mcp",
        timeout: float = 5.0,
    ):
        """
        Initialize optional Graphiti backend.
        
        Args:
            endpoint: Graphiti MCP server URL. If None, tries default.
            group_id: Graphiti group for multi-tenant isolation
            timeout: Connection timeout in seconds
        """
        self._endpoint = endpoint or "http://localhost:8083/mcp/"
        self._group_id = group_id
        self._timeout = timeout
        self._enabled = False
        self._client: Optional[httpx.AsyncClient] = None
        self._check_connection()
    
    def _check_connection(self) -> None:
        """Check if Graphiti MCP server is reachable."""
        if not HAS_HTTPX:
            logger.info("Graphiti backend: httpx not installed, disabled")
            return
        
        try:
            # Quick sync check — just test status endpoint
            # Using synchronous httpx call for init
            client = httpx.Client(timeout=self._timeout)
            try:
                resp = client.get(f"{self._endpoint.rstrip('/')}/status")
                if resp.status_code == 200 or resp.status_code == 405:
                    self._enabled = True
                    self._client = httpx.AsyncClient(timeout=self._timeout)
                    logger.info(f"Graphiti backend connected: {self._endpoint}")
                else:
                    logger.info(f"Graphiti backend not available (status {resp.status_code})")
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError):
                self._async_client = None
                logger.info("Graphiti backend: no server running, disabled (safe to ignore)")
            finally:
                client.close()
        except Exception:
            self._enabled = False
            logger.debug("Graphiti backend initialization failed, disabled")
    
    @property
    def enabled(self) -> bool:
        """Whether the Graphiti backend is active."""
        return self._enabled
    
    def record_success(
        self,
        genre: str,
        params: Dict[str, Any],
        quality: int = 5,
    ) -> bool:
        """
        Record a successful generation as a graph episode.
        
        Args:
            genre: Genre identifier
            params: Generation parameters (key, tempo, density, etc.)
            quality: User rating (1-10)
            
        Returns:
            True if recorded successfully, False if backend unavailable
        """
        if not self._enabled or not self._client:
            return False
        
        try:
            # Build structured episode text for entity extraction
            episode_text = (
                f"Music generation for {genre}: "
                + ", ".join(f"{k}={v}" for k, v in params.items())
                + f" | quality={quality}/10"
            )
            
            import httpx
            client = httpx.Client(timeout=self._timeout)
            try:
                response = client.post(
                    f"{self._endpoint.rstrip('/')}/mcp/tools/add_episode",
                    json={
                        "text": episode_text,
                        "group_id": self._group_id,
                    },
                )
                return response.status_code in (200, 201)
            except Exception:
                return False
            finally:
                client.close()
        except Exception as e:
            logger.debug(f"Graphiti record failed: {e}")
            return False
    
    def recommend(self, genre: str) -> Dict[str, Any]:
        """
        Query Graphiti for optimal parameters based on past patterns.
        
        Searches the knowledge graph for patterns matching this genre
        and returns aggregated parameter recommendations.
        
        Args:
            genre: Genre to query for
            
        Returns:
            Dict of recommended parameter values (empty if unavailable)
        """
        if not self._enabled:
            return {}
        
        try:
            # Search for patterns with this genre tag
            import httpx
            client = httpx.Client(timeout=self._timeout)
            try:
                response = client.post(
                    f"{self._endpoint.rstrip('/')}/mcp/tools/search_nodes",
                    json={
                        "query": f"genre:{genre} quality > 5",
                        "group_id": self._group_id,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    # Parse results into recommendations
                    return self._parse_recommendations(data)
            except Exception:
                return {}
            finally:
                client.close()
        except Exception:
            return {}
        
        return {}
    
    def search_similar(
        self,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for patterns similar to the query.
        
        Uses Graphiti's semantic/hybrid search across entities.
        
        Args:
            query: Natural language description ("dark Fm bass 126bpm")
            limit: Maximum results
            
        Returns:
            List of matching pattern entries
        """
        if not self._enabled:
            return []
        
        try:
            import httpx
            client = httpx.Client(timeout=self._timeout)
            try:
                response = client.post(
                    f"{self._endpoint.rstrip('/')}/mcp/tools/search_nodes",
                    json={
                        "query": query,
                        "group_id": self._group_id,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])[:limit]
            except Exception:
                return []
            finally:
                client.close()
        except Exception:
            return []
        
        return []
    
    def get_history(
        self,
        genre: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent generation episodes from Graphiti.
        
        Args:
            genre: Optional genre filter
            limit: Maximum entries
            
        Returns:
            List of episode dicts
        """
        if not self._enabled:
            return []
        
        try:
            import httpx
            client = httpx.Client(timeout=self._timeout)
            try:
                response = client.post(
                    f"{self._endpoint.rstrip('/')}/mcp/tools/get_episodes",
                    json={
                        "group_id": self._group_id,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    episodes = data.get("episodes", [])
                    if genre:
                        episodes = [e for e in episodes if genre in str(e.get("text", ""))]
                    return episodes[-limit:]
            except Exception:
                return []
            finally:
                client.close()
        except Exception:
            return []
        
        return []
    
    def clear(self) -> bool:
        """Clear all stored patterns in this group."""
        if not self._enabled:
            return False
        
        try:
            import httpx
            client = httpx.Client(timeout=self._timeout)
            try:
                response = client.post(
                    f"{self._endpoint.rstrip('/')}/mcp/tools/clear_graph",
                    json={"group_id": self._group_id},
                )
                return response.status_code == 200
            except Exception:
                return False
            finally:
                client.close()
        except Exception:
            return False
    
    def _parse_recommendations(self, data: Dict) -> Dict[str, Any]:
        """Extract parameter recommendations from graph search results."""
        recommendations = {}
        try:
            results = data.get("results", []) if isinstance(data, dict) else []
            if not results:
                return {}
            
            # Aggregate parameters from matching patterns
            params: Dict[str, List[float]] = {}
            for result in results:
                text = result.get("text", "") if isinstance(result, dict) else str(result)
                # Extract k=v pairs from episode text
                for part in text.split(","):
                    if "=" in part:
                        key, value = part.split("=", 1)
                        key = key.strip()
                        try:
                            val = float(value.strip())
                            if key not in params:
                                params[key] = []
                            params[key].append(val)
                        except ValueError:
                            pass
            
            # Average numeric parameters
            for key, values in params.items():
                if values:
                    recommendations[key] = sum(values) / len(values)
            
        except Exception:
            pass
        
        return recommendations


def create_memory_backend(
    endpoint: Optional[str] = None,
    group_id: str = "ableton-mcp",
) -> GraphitiMemoryBackend:
    """
    Convenience factory: create Graphiti backend, gracefully fall back.
    
    Usage:
        backend = create_memory_backend()
        if backend.enabled:
            # Graphiti is running
        else:
            # In-memory fallback (use standard MemorySystem)
    """
    backend = GraphitiMemoryBackend(endpoint=endpoint, group_id=group_id)
    if backend.enabled:
        logger.info("Graphiti memory backend active")
    else:
        logger.info("Using in-memory fallback (no Graphiti server detected)")
    return backend
