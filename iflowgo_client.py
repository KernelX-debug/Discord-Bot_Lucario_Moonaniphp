import json
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

import requests


NEARBY_ENDPOINT = "https://pokecoords.iflowgo.com/iflowgopokecoords/api/v1/nearby"
GLOBAL_SEARCH_ENDPOINT = "https://pokecoords.iflowgo.com/iflowgopokecoords/api/v1/pokemon-search"
POKEAPI_POKEMON_ENDPOINT = "https://pokeapi.co/api/v2/pokemon"
DEFAULT_HEADERS = {"User-Agent": "Lucario Discord Bot/1.0", "Accept": "application/json"}
UTC_PLUS_7 = timezone(timedelta(hours=7))


@dataclass(frozen=True)
class IFlowGoSpawn:
    pokemon_name: str
    pokemon_id: int
    coords: str
    cp: int
    level: int
    iv_percent: float
    attack: int
    defense: int
    hp: int
    gender: int
    end_time: str
    country: str
    city: str
    region: str
    spawn_id: str

    @property
    def maps_url(self) -> str:
        return f"https://maps.google.com/?q={self.coords}"

    @property
    def unique_key(self) -> str:
        return self.spawn_id or f"{self.pokemon_id}|{self.coords}|{self.end_time}"


@dataclass(frozen=True)
class IFlowGoSearchResult:
    spawns: List[IFlowGoSpawn]
    total_hotspots: int
    failed_hotspots: int
    source: str = "hotspots"


class IFlowGoClient:
    """Busca spawns globales consultando los hotspots guardados en el proyecto."""

    def __init__(
        self,
        hotspots_path: Path,
        timeout: int = 12,
        max_workers: int = 4,
        cache_ttl_seconds: int = 120,
        hotspot_limit: Optional[int] = None,
    ) -> None:
        self.hotspots_path = hotspots_path
        self.timeout = timeout
        self.max_workers = max(1, max_workers)
        self.cache_ttl_seconds = cache_ttl_seconds
        self.hotspot_limit = hotspot_limit
        self._hotspots = self._load_hotspots()
        self._pokemon_id_cache = {}  # type: Dict[str, Tuple[float, int, str]]
        self._search_cache = {}  # type: Dict[Tuple[int, int], Tuple[float, IFlowGoSearchResult]]
        self._search_locks = {}  # type: Dict[Tuple[int, int], Lock]
        self._search_locks_guard = Lock()

    def _load_hotspots(self) -> List[Dict[str, Any]]:
        try:
            payload = json.loads(self.hotspots_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"No pude cargar hotspots.json: {exc}") from exc

        hotspots = []
        seen_coords = set()
        for country in payload.get("countries", []):
            if not isinstance(country, dict):
                continue
            for spot in country.get("spots", []):
                if not isinstance(spot, dict):
                    continue
                try:
                    lat = float(spot["lat"])
                    lon = float(spot["lon"])
                except (KeyError, TypeError, ValueError):
                    continue
                coords_key = (lat, lon)
                if coords_key in seen_coords:
                    continue
                seen_coords.add(coords_key)
                hotspots.append({
                    "lat": lat,
                    "lon": lon,
                    "country_code": str(spot.get("country_code", "")).upper() or "Unknown",
                    "city": str(spot.get("city", "")).strip() or "Unknown",
                    "region": str(spot.get("region", "")).strip() or "Unknown",
                })

        if not hotspots:
            raise RuntimeError("hotspots.json no contiene coordenadas validas.")
        return hotspots[: self.hotspot_limit] if self.hotspot_limit else hotspots

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = unicodedata.normalize("NFKD", name.strip().lower())
        normalized = "".join(char for char in normalized if not unicodedata.combining(char))
        return normalized.replace(" ", "-")

    def resolve_pokemon(self, pokemon_name: str) -> Tuple[int, str]:
        normalized_name = self._normalize_name(pokemon_name)
        if not normalized_name:
            raise ValueError("Debes indicar el nombre del Pokemon.")

        cached = self._pokemon_id_cache.get(normalized_name)
        now = time.monotonic()
        if cached and now - cached[0] < 24 * 60 * 60:
            return cached[1], cached[2]

        response = requests.get(
            f"{POKEAPI_POKEMON_ENDPOINT}/{normalized_name}",
            headers=DEFAULT_HEADERS,
            timeout=self.timeout,
        )
        if response.status_code == 404:
            raise ValueError(f"No reconozco el Pokemon '{pokemon_name}'. Usa su nombre en ingles.")
        response.raise_for_status()
        payload = response.json()
        pokemon_id = int(payload["id"])
        display_name = str(payload.get("name", normalized_name)).replace("-", " ").title()
        self._pokemon_id_cache[normalized_name] = (now, pokemon_id, display_name)
        return pokemon_id, display_name

    def _fetch_hotspot(
        self,
        hotspot: Dict[str, Any],
        pokemon_id: int,
        min_iv: int,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        params = {
            "lat": hotspot["lat"],
            "lon": hotspot["lon"],
            "radius_km": 25,
            "layers": "spawns",
            "limit": 800,
            "pokemon_id": pokemon_id,
            "min_iv": min_iv,
        }
        response = requests.get(
            NEARBY_ENDPOINT,
            params=params,
            headers=DEFAULT_HEADERS,
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        spawns = payload.get("spawns", []) if isinstance(payload, dict) else []
        return hotspot, spawns if isinstance(spawns, list) else []

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _safe_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _format_expiration(value: Any) -> str:
        raw_value = str(value or "").strip()
        if not raw_value:
            return ""
        try:
            parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
        except ValueError:
            return raw_value
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(UTC_PLUS_7)
        return parsed.strftime("%Y-%m-%d %H:%M:%S")

    def _fetch_global_page(self, pokemon_id: int, min_iv: int, page: int) -> Tuple[int, List[Dict[str, Any]]]:
        response = requests.get(
            GLOBAL_SEARCH_ENDPOINT,
            params={
                "sort_by": "iv_desc",
                "page": page,
                "page_size": 25,
                "min_iv": min_iv,
                "max_iv": 100,
                "pokemon_id": pokemon_id,
            },
            headers=DEFAULT_HEADERS,
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("iFlowGo respondio con un formato inesperado.")
        items = payload.get("items", [])
        total_pages = self._safe_int(payload.get("total_pages"))
        if total_pages < 1:
            total = self._safe_int(payload.get("total"))
            page_size = max(1, self._safe_int(payload.get("page_size")))
            total_pages = max(1, (total + page_size - 1) // page_size)
        return total_pages, items if isinstance(items, list) else []

    def _search_global_pokemon(self, pokemon_id: int, display_name: str, min_iv: int) -> IFlowGoSearchResult:
        spawns_by_id = {}  # type: Dict[str, IFlowGoSpawn]
        page = 1
        total_pages = 1

        while page <= total_pages:
            total_pages, rows = self._fetch_global_page(pokemon_id, min_iv, page)
            if not rows:
                break

            for row in rows:
                if not isinstance(row, dict):
                    continue
                iv_percent = self._safe_float(row.get("percent_iv"))
                if self._safe_int(row.get("pokemon_id")) != pokemon_id or iv_percent < min_iv:
                    continue
                lat = row.get("lat")
                lon = row.get("lon")
                if lat is None or lon is None:
                    continue
                spawn = IFlowGoSpawn(
                    pokemon_name=display_name,
                    pokemon_id=pokemon_id,
                    coords=f"{lat},{lon}",
                    cp=self._safe_int(row.get("cp")),
                    level=self._safe_int(row.get("level")),
                    iv_percent=iv_percent,
                    attack=self._safe_int(row.get("attack_iv")),
                    defense=self._safe_int(row.get("defense_iv")),
                    hp=self._safe_int(row.get("stamina_iv")),
                    gender=self._safe_int(row.get("gender")),
                    end_time=self._format_expiration(row.get("expires_at")),
                    country="Global",
                    city="",
                    region="",
                    spawn_id=str(row.get("id", "")).strip(),
                )
                existing = spawns_by_id.get(spawn.unique_key)
                if existing is None or spawn.iv_percent > existing.iv_percent:
                    spawns_by_id[spawn.unique_key] = spawn

            page += 1

        return IFlowGoSearchResult(
            spawns=sorted(
                spawns_by_id.values(),
                key=lambda spawn: (spawn.iv_percent, spawn.end_time),
                reverse=True,
            ),
            total_hotspots=0,
            failed_hotspots=0,
            source="global",
        )

    def search_pokemon(
        self,
        pokemon_name: str,
        min_iv: int,
        minimum_results: int = 0,
    ) -> IFlowGoSearchResult:
        if not 0 <= min_iv <= 100:
            raise ValueError("`miniv` debe estar entre 0 y 100.")
        if minimum_results < 0:
            raise ValueError("La cantidad minima no puede ser negativa.")

        pokemon_id, display_name = self.resolve_pokemon(pokemon_name)
        cache_key = (pokemon_id, min_iv)
        with self._search_locks_guard:
            search_lock = self._search_locks.setdefault(cache_key, Lock())

        # A duplicate slash command waits for the first scan, then reuses its cache :'v
        with search_lock:
            now = time.monotonic()
            cached = self._search_cache.get(cache_key)
            if (
                cached
                and now - cached[0] < self.cache_ttl_seconds
                and (len(cached[1].spawns) >= minimum_results or cached[1].source != "global")
            ):
                return cached[1]

            global_result = None  # type: Optional[IFlowGoSearchResult]
            try:
                result = self._search_global_pokemon(pokemon_id, display_name, min_iv)
            except (requests.RequestException, ValueError) as exc:
                print(f"[iFlowGo] La busqueda global fallo; usare hotspots: {type(exc).__name__}: {exc}")
            else:
                if len(result.spawns) >= minimum_results:
                    self._search_cache[cache_key] = (now, result)
                    return result
                global_result = result
                print(
                    f"[iFlowGo] La busqueda global encontro {len(result.spawns)} resultado(s); "
                    f"completare con hotspots para llegar a {minimum_results}."
                )

            spawns_by_id = {
                spawn.unique_key: spawn for spawn in global_result.spawns
            } if global_result else {}  # type: Dict[str, IFlowGoSpawn]
            failed_hotspots = 0
            with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="iflowgo") as executor:
                futures = [
                    executor.submit(self._fetch_hotspot, hotspot, pokemon_id, min_iv)
                    for hotspot in self._hotspots
                ]
                for future in as_completed(futures):
                    try:
                        hotspot, rows = future.result()
                    except requests.RequestException as exc:
                        failed_hotspots += 1
                        print(f"[iFlowGo] Error consultando hotspot: {type(exc).__name__}: {exc}")
                        continue
                    except (TypeError, ValueError, KeyError) as exc:
                        failed_hotspots += 1
                        print(f"[iFlowGo] Respuesta invalida de hotspot: {type(exc).__name__}: {exc}")
                        continue

                    for row in rows:
                        if not isinstance(row, dict):
                            continue
                        iv_percent = self._safe_float(row.get("percent_iv"))
                        if self._safe_int(row.get("pokemon_id")) != pokemon_id or iv_percent < min_iv:
                            continue
                        lat = row.get("lat")
                        lon = row.get("lon")
                        if lat is None or lon is None:
                            continue
                        spawn = IFlowGoSpawn(
                            pokemon_name=display_name,
                            pokemon_id=pokemon_id,
                            coords=f"{lat},{lon}",
                            cp=self._safe_int(row.get("cp")),
                            level=self._safe_int(row.get("level")),
                            iv_percent=iv_percent,
                            attack=self._safe_int(row.get("attack_iv")),
                            defense=self._safe_int(row.get("defense_iv")),
                            hp=self._safe_int(row.get("stamina_iv")),
                            gender=self._safe_int(row.get("gender")),
                            end_time=self._format_expiration(row.get("expires_at")),
                            country=str(hotspot["country_code"]),
                            city=str(hotspot["city"]),
                            region=str(hotspot["region"]),
                            spawn_id=str(row.get("id", "")).strip(),
                        )
                        existing = spawns_by_id.get(spawn.unique_key)
                        if existing is None or spawn.iv_percent > existing.iv_percent:
                            spawns_by_id[spawn.unique_key] = spawn

            result = IFlowGoSearchResult(
                spawns=sorted(
                    spawns_by_id.values(),
                    key=lambda spawn: (spawn.iv_percent, spawn.end_time),
                    reverse=True,
                ),
                total_hotspots=len(self._hotspots),
                failed_hotspots=failed_hotspots,
                source="global+hotspots" if global_result else "hotspots",
            )
            self._search_cache[cache_key] = (now, result)
            return result
