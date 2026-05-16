"""Phase 4 API 結合テスト — 全 MUST エンドポイントの動作確認."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch

from api.main import app
from api.schemas import (
    HealthResponseData,
    IngestUrlResponseData,
    IngestSearchResponseData,
    SearchTechnologiesResponseData,
    TechnologiesListResponseData,
    TechnologyDetailSchema,
    CompareResponseData,
    RecommendResponseData,
)


# --- Fixtures ---

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


# Helper: DBセッションモック
def make_db_mock():
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)
    return mock_db


# ============================================================
# F001: ヘルスチェック (GET /api/v1/health)
# ============================================================

class TestHealthEndpoint:
    """GET /api/v1/health — ヘルスチェック."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, client):
        """F001: ヘルスエンドポイントが200を返す."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 1
        with patch("db.session.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_get_db.return_value = _async_gen(mock_db)
            response = await client.get("/api/v1/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_success_field(self, client):
        """F001: ヘルスレスポンスの success フィールドが True."""
        mock_result = MagicMock()
        with patch("db.session.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_get_db.return_value = _async_gen(mock_db)
            response = await client.get("/api/v1/health")
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_health_version(self, client):
        """F001: バージョン番号が 0.1.0."""
        with patch("db.session.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute = AsyncMock()
            mock_get_db.return_value = _async_gen(mock_db)
            response = await client.get("/api/v1/health")
        data = response.json()
        assert data["data"]["version"] == "0.1.0"


# ============================================================
# F003: バリデーション — URL収集リクエスト (F001)
# ============================================================

class TestIngestUrlValidation:
    """POST /api/v1/ingest/url — バリデーション."""

    @pytest.mark.asyncio
    async def test_ingest_url_invalid_scheme_returns_422(self, client):
        """F001: http/https 以外のURLは422エラー."""
        response = await client.post(
            "/api/v1/ingest/url",
            json={"url": "ftp://example.com", "collection_mode": "standard"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ingest_url_invalid_mode_returns_422(self, client):
        """F001: 不正な collection_mode は422エラー."""
        response = await client.post(
            "/api/v1/ingest/url",
            json={"url": "https://example.com", "collection_mode": "ultra"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ingest_url_tag_too_long_returns_422(self, client):
        """F001: 51文字以上のタグは422エラー."""
        response = await client.post(
            "/api/v1/ingest/url",
            json={"url": "https://example.com", "tags": ["a" * 51]},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ingest_url_too_many_tags_returns_422(self, client):
        """F001: 21個以上のタグは422エラー."""
        response = await client.post(
            "/api/v1/ingest/url",
            json={"url": "https://example.com", "tags": [f"tag{i}" for i in range(21)]},
        )
        assert response.status_code == 422


# ============================================================
# F003: 検索 (POST /api/v1/search/technologies) バリデーション
# ============================================================

class TestSearchValidation:
    """POST /api/v1/search/technologies — バリデーション."""

    @pytest.mark.asyncio
    async def test_search_empty_query_returns_422(self, client):
        """F003: 空クエリは422エラー."""
        response = await client.post(
            "/api/v1/search/technologies",
            json={"query": ""},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_invalid_mode_returns_422(self, client):
        """F003: 不正なsearch modeは422エラー."""
        response = await client.post(
            "/api/v1/search/technologies",
            json={"query": "test", "mode": "invalid_mode"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_valid_modes(self, client):
        """F003: 有効なsearch modeは422エラーを返さない（DB結果は空でよい）."""
        valid_modes = ["keyword", "problem_search", "domain", "condition"]
        for mode in valid_modes:
            with patch("api.routers.search.hybrid_search") as mock_search:
                mock_search.return_value = ([], 0)
                with patch("db.session.get_db") as mock_get_db:
                    mock_db = AsyncMock()
                    mock_get_db.return_value = _async_gen(mock_db)
                    response = await client.post(
                        "/api/v1/search/technologies",
                        json={"query": "test", "mode": mode},
                    )
            assert response.status_code == 200, f"mode={mode} should return 200"


# ============================================================
# F003: 検索 — 正常系
# ============================================================

class TestSearchNormalCase:
    """POST /api/v1/search/technologies — 正常系."""

    @pytest.mark.asyncio
    async def test_search_returns_api_response_structure(self, client):
        """F003: 検索結果がApiResponse構造で返る."""
        mock_result = MagicMock()
        mock_result.technology_id = "uuid-1"
        mock_result.name = "Behavior Tree"
        mock_result.fit_score = 0.9
        mock_result.summary = "状態管理パターン"
        mock_result.why_relevant = "Matches query: test"
        mock_result.benefits = ["構造化されたAI行動"]
        mock_result.drawbacks = ["複雑さ"]
        mock_result.alternatives = []
        mock_result.domains = ["AI"]
        mock_result.item_type = "technique"
        mock_result.maturity_level = "mature"

        with patch("api.routers.search.hybrid_search") as mock_search:
            mock_search.return_value = ([mock_result], 1)
            with patch("db.session.get_db") as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = _async_gen(mock_db)
                response = await client.post(
                    "/api/v1/search/technologies",
                    json={"query": "test", "mode": "keyword"},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "results" in data["data"]

    @pytest.mark.asyncio
    async def test_search_pagination_meta(self, client):
        """F003: 検索レスポンスにmeta（ページネーション情報）が含まれる."""
        with patch("api.routers.search.hybrid_search") as mock_search:
            mock_search.return_value = ([], 0)
            with patch("db.session.get_db") as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = _async_gen(mock_db)
                response = await client.post(
                    "/api/v1/search/technologies",
                    json={"query": "test", "mode": "keyword", "limit": 10, "offset": 0},
                )

        data = response.json()
        assert "meta" in data
        assert "total" in data["meta"]


# ============================================================
# F004: 技術一覧 (GET /api/v1/technologies)
# ============================================================

class TestTechnologiesListEndpoint:
    """GET /api/v1/technologies — 技術一覧."""

    @pytest.mark.asyncio
    async def test_list_returns_200(self, client):
        """F004: 技術一覧が200を返す."""
        mock_count = MagicMock()
        mock_count.scalar_one.return_value = 0
        mock_items = MagicMock()
        mock_items.scalars.return_value.all.return_value = []

        with patch("db.session.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute = AsyncMock(side_effect=[mock_count, mock_items])
            mock_get_db.return_value = _async_gen(mock_db)
            response = await client.get("/api/v1/technologies")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_response_structure(self, client):
        """F004: 技術一覧レスポンスがitems・totalを含む."""
        mock_count = MagicMock()
        mock_count.scalar_one.return_value = 0
        mock_items = MagicMock()
        mock_items.scalars.return_value.all.return_value = []

        with patch("db.session.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute = AsyncMock(side_effect=[mock_count, mock_items])
            mock_get_db.return_value = _async_gen(mock_db)
            response = await client.get("/api/v1/technologies")

        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]
        assert "total" in data["data"]

    @pytest.mark.asyncio
    async def test_list_invalid_limit_returns_422(self, client):
        """F004: limitが0の場合は422エラー."""
        response = await client.get("/api/v1/technologies?limit=0")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_invalid_offset_returns_422(self, client):
        """F004: offsetが負の場合は422エラー."""
        response = await client.get("/api/v1/technologies?offset=-1")
        assert response.status_code == 422


# ============================================================
# F005: 技術詳細 (GET /api/v1/technologies/{id})
# ============================================================

class TestTechnologyDetailEndpoint:
    """GET /api/v1/technologies/{id} — 技術詳細."""

    @pytest.mark.asyncio
    async def test_not_found_returns_404(self, client):
        """F005: 存在しないIDは404エラー."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        with patch("db.session.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_get_db.return_value = _async_gen(mock_db)
            response = await client.get("/api/v1/technologies/non-existent-id")

        assert response.status_code == 404


# ============================================================
# F007: 技術比較 (POST /api/v1/compare) — バリデーション
# ============================================================

class TestCompareValidation:
    """POST /api/v1/compare — バリデーション."""

    @pytest.mark.asyncio
    async def test_compare_single_tech_returns_422(self, client):
        """F007: 1件のみのリストは422エラー（min_length=2）."""
        response = await client.post(
            "/api/v1/compare",
            json={"technologies": ["FSM"]},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_compare_empty_list_returns_422(self, client):
        """F007: 空リストは422エラー."""
        response = await client.post(
            "/api/v1/compare",
            json={"technologies": []},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_compare_too_many_returns_422(self, client):
        """F007: 11件以上は422エラー（max_length=10）."""
        response = await client.post(
            "/api/v1/compare",
            json={"technologies": [f"tech{i}" for i in range(11)]},
        )
        assert response.status_code == 422


# ============================================================
# F008: 技術推薦 (POST /api/v1/recommend) — バリデーション
# ============================================================

class TestRecommendValidation:
    """POST /api/v1/recommend — バリデーション."""

    @pytest.mark.asyncio
    async def test_recommend_short_description_returns_422(self, client):
        """F008: 10文字未満の説明は422エラー."""
        response = await client.post(
            "/api/v1/recommend",
            json={"problem_description": "short"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_recommend_invalid_limit_returns_422(self, client):
        """F008: limitが21以上は422エラー."""
        response = await client.post(
            "/api/v1/recommend",
            json={
                "problem_description": "有効な問題の説明文です",
                "limit": 21,
            },
        )
        assert response.status_code == 422


# ============================================================
# APIレスポンス構造の一貫性
# ============================================================

class TestApiResponseConsistency:
    """全エンドポイントのAPIレスポンス一貫性."""

    @pytest.mark.asyncio
    async def test_error_response_has_success_false(self, client):
        """422エラーのレスポンスにはdetailフィールドが含まれる（FastAPIデフォルト）."""
        response = await client.post(
            "/api/v1/ingest/url",
            json={"url": "not-a-url"},
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_health_response_has_required_fields(self, client):
        """ヘルスレスポンスにstatus・db・versionフィールドが含まれる."""
        with patch("db.session.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute = AsyncMock()
            mock_get_db.return_value = _async_gen(mock_db)
            response = await client.get("/api/v1/health")

        data = response.json()
        assert data["data"]["status"] in ("ok", "degraded")
        assert data["data"]["db"] in ("ok", "error")
        assert "version" in data["data"]


# ============================================================
# Helper
# ============================================================

async def _async_gen(value):
    """非同期ジェネレータのヘルパー（get_dbのモック用）."""
    yield value
