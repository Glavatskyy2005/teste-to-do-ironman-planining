"""
Servidor MCP para o intervals.icu.

Expõe os dados de treino do António (atividades, wellness, eventos planeados,
perfil/zonas) como ferramentas MCP, para o agente "treino-ironman" (ou
"claudio") poder consultar dados reais em vez de perguntar tudo na conversa.

Autenticação com o intervals.icu: API key oficial (Settings > Developer
Settings em https://intervals.icu), sem necessidade de password do Garmin.
O intervals.icu já sincroniza automaticamente com o Garmin, por isso os
treinos feitos no Garmin aparecem aqui.

Este servidor corre como um serviço HTTP (streamable-http) para poder ser
registado como "custom connector" em claude.ai. Protegido por um token
bearer simples (MCP_AUTH_TOKEN) para que não fique aberto a qualquer pessoa
que descubra o URL.
"""

import os
import sys
from datetime import date, timedelta

import requests
import uvicorn
from requests.auth import HTTPBasicAuth
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from mcp.server.fastmcp import FastMCP

# --------------------------------------------------------------------------
# Configuração
# --------------------------------------------------------------------------

API_KEY = os.environ.get("INTERVALS_API_KEY")
ATHLETE_ID = os.environ.get("INTERVALS_ATHLETE_ID", "0")  # "0" = atleta autenticado
AUTH_TOKEN = os.environ.get("MCP_AUTH_TOKEN")  # token bearer para proteger o servidor
PORT = int(os.environ.get("PORT", "8000"))

if not API_KEY:
    print(
        "ERRO: falta a variável de ambiente INTERVALS_API_KEY "
        "(vai a intervals.icu > Settings > Developer Settings para gerar uma).",
        file=sys.stderr,
    )
    sys.exit(1)

if not AUTH_TOKEN:
    print(
        "AVISO: MCP_AUTH_TOKEN não está definido — o servidor vai ficar "
        "acessível sem autenticação a quem souber o URL. Define um token "
        "antes de expor isto publicamente.",
        file=sys.stderr,
    )

BASE_URL = "https://intervals.icu/api/v1"
BASIC_AUTH = HTTPBasicAuth("API_KEY", API_KEY)

mcp = FastMCP("intervals-icu")


def _get(path: str, params: dict | None = None) -> dict | list:
    resp = requests.get(f"{BASE_URL}{path}", params=params, auth=BASIC_AUTH, timeout=20)
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------------------------
# Ferramentas MCP
# --------------------------------------------------------------------------


@mcp.tool()
def list_activities(oldest: str = "", newest: str = "", limit: int = 20) -> list[dict]:
    """Lista as atividades de treino registadas no intervals.icu.

    Args:
        oldest: data mais antiga, formato YYYY-MM-DD. Vazio = últimos 30 dias.
        newest: data mais recente, formato YYYY-MM-DD. Vazio = hoje.
        limit: número máximo de atividades a devolver.
    """
    if not newest:
        newest = date.today().isoformat()
    if not oldest:
        oldest = (date.today() - timedelta(days=30)).isoformat()

    data = _get(f"/athlete/{ATHLETE_ID}/activities", {"oldest": oldest, "newest": newest})
    activities = data[:limit] if isinstance(data, list) else []
    return [
        {
            "id": a.get("id"),
            "name": a.get("name"),
            "type": a.get("type"),
            "date": a.get("start_date_local"),
            "distance_m": a.get("distance"),
            "duration_s": a.get("moving_time"),
            "avg_hr": a.get("average_heartrate"),
            "avg_power_w": a.get("icu_average_watts"),
            "training_load": a.get("icu_training_load"),
            "rpe": a.get("perceived_exertion"),
        }
        for a in activities
    ]


@mcp.tool()
def get_activity(activity_id: str) -> dict:
    """Devolve o detalhe completo de uma atividade específica (splits, zonas, potência, etc.)."""
    return _get(f"/activity/{activity_id}")


@mcp.tool()
def get_wellness(oldest: str = "", newest: str = "") -> list[dict]:
    """Devolve dados diários de wellness: sono, HRV, FC em repouso, peso, fadiga/forma.

    Args:
        oldest: data mais antiga, formato YYYY-MM-DD. Vazio = últimos 14 dias.
        newest: data mais recente, formato YYYY-MM-DD. Vazio = hoje.
    """
    if not newest:
        newest = date.today().isoformat()
    if not oldest:
        oldest = (date.today() - timedelta(days=14)).isoformat()
    data = _get(f"/athlete/{ATHLETE_ID}/wellness", {"oldest": oldest, "newest": newest})
    return data if isinstance(data, list) else [data]


@mcp.tool()
def get_upcoming_events(oldest: str = "", newest: str = "") -> list[dict]:
    """Devolve os treinos planeados / eventos no calendário do intervals.icu.

    Args:
        oldest: data mais antiga, formato YYYY-MM-DD. Vazio = hoje.
        newest: data mais recente, formato YYYY-MM-DD. Vazio = daqui a 14 dias.
    """
    if not oldest:
        oldest = date.today().isoformat()
    if not newest:
        newest = (date.today() + timedelta(days=14)).isoformat()
    data = _get(f"/athlete/{ATHLETE_ID}/events", {"oldest": oldest, "newest": newest})
    return data if isinstance(data, list) else [data]


@mcp.tool()
def get_athlete_profile() -> dict:
    """Devolve o perfil do atleta: zonas de FC/potência, FTP, limiares configurados no intervals.icu."""
    return _get(f"/athlete/{ATHLETE_ID}")


# --------------------------------------------------------------------------
# Servidor HTTP com autenticação simples por bearer token
# --------------------------------------------------------------------------


class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if AUTH_TOKEN:
            header = request.headers.get("authorization", "")
            if header != f"Bearer {AUTH_TOKEN}":
                return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)


def build_app():
    app = mcp.streamable_http_app()
    app.add_middleware(BearerAuthMiddleware)
    return app


if __name__ == "__main__":
    app = build_app()
    uvicorn.run(app, host="0.0.0.0", port=PORT)
