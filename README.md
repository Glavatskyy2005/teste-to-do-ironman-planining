# Servidor MCP — intervals.icu

Liga os teus dados de treino do intervals.icu (que já sincroniza automaticamente
com o Garmin) ao agente **treino-ironman** / **claudio**, para eles poderem
consultar atividades, wellness (sono, HRV, FC repouso), treinos planeados e o
teu perfil de zonas, em vez de teres de descrever tudo na conversa.

Usa a **API oficial do intervals.icu** com uma chave de API pessoal —
diferente de uma integração com o Garmin, não precisa da tua password em lado
nenhum, e podes revogar a chave a qualquer momento em intervals.icu.

## 1. Gerar a chave de API

1. Entra em https://intervals.icu
2. Vai a **Settings → Developer Settings**
3. Copia a tua **API Key**
4. (Opcional) Confirma o teu **Athlete ID** no URL do teu perfil (`intervals.icu/athlete/iXXXXXX`) — se não souberes, deixa `INTERVALS_ATHLETE_ID=0`, que corresponde ao atleta autenticado pela própria chave.

## 2. Testar localmente

```bash
cd intervals-mcp-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edita o .env e preenche INTERVALS_API_KEY, MCP_AUTH_TOKEN, etc.

export $(cat .env | xargs)   # ou usa python-dotenv / a forma que preferires
python server.py
```

Devias ver o servidor a arrancar em `http://0.0.0.0:8000`. Testa com:

```bash
curl -H "Authorization: Bearer <o-teu-MCP_AUTH_TOKEN>" http://localhost:8000/mcp
```

Se o teu `MCP_AUTH_TOKEN` estiver certo, isto não deve devolver `401`.

## 3. Alojar num sítio acessível publicamente

Este servidor tem de ficar a correr **de forma permanente** e acessível por
HTTPS para o Claude conseguir ligar-se a ele — não pode ficar só na tua
máquina local a não ser que uses um túnel (ex: `ngrok`, `cloudflared`) enquanto
o usas.

Opções simples (todas têm planos gratuitos ou muito baratos):

- **Fly.io** — `fly launch` na pasta do projeto (deteta o Dockerfile automaticamente), depois `fly secrets set INTERVALS_API_KEY=... MCP_AUTH_TOKEN=...`
- **Render.com** — "New Web Service" a partir do teu repositório Git, define as variáveis de ambiente no painel
- **Railway.app** — semelhante ao Render, deploy direto do Dockerfile
- Um VPS próprio (ex: DigitalOcean, Hetzner) com Docker instalado: `docker build -t intervals-mcp . && docker run -d -p 8000:8000 --env-file .env intervals-mcp`, com um proxy reverso (Caddy/Nginx) à frente para teres HTTPS

Em qualquer opção: **nunca** metas a `INTERVALS_API_KEY` ou o `MCP_AUTH_TOKEN`
diretamente no código — usa sempre variáveis de ambiente/secrets do serviço.

## 4. Registar como custom connector no Claude

1. Em claude.ai (ou na app), vai a **Settings → Connectors → Add custom connector**
2. URL: o endereço público do teu servidor (ex: `https://intervals-mcp.fly.dev/mcp`)
3. Header de autenticação: `Authorization: Bearer <o-teu-MCP_AUTH_TOKEN>`
4. Dá-lhe um nome (ex: `intervals-icu`) — as ferramentas vão aparecer como `mcp__intervals-icu__list_activities`, etc.
5. Ativa o conector nesta conversa/organização

## Ferramentas disponíveis

| Ferramenta | O que faz |
|---|---|
| `list_activities(oldest, newest, limit)` | Lista atividades num intervalo de datas |
| `get_activity(activity_id)` | Detalhe completo de uma atividade (splits, zonas, potência) |
| `get_wellness(oldest, newest)` | Sono, HRV, FC em repouso, peso, forma/fadiga |
| `get_upcoming_events(oldest, newest)` | Treinos planeados no calendário do intervals.icu |
| `get_athlete_profile()` | Zonas de FC/potência, FTP, limiares configurados |

## Avisos importantes

- **Segurança**: o `MCP_AUTH_TOKEN` é a única coisa que impede qualquer pessoa
  com o URL de aceder aos teus dados de treino — usa uma string longa e
  aleatória, e não a partilhes.
- **Sem MFA/password do Garmin envolvida** — esta via usa só a API oficial do
  intervals.icu, por isso é bastante mais segura do que uma integração direta
  com o Garmin Connect (que não tem API pública para contas pessoais).
- Este é um ponto de partida funcional, mas não foi testado com a tua conta
  real (não tenho as tuas credenciais nem devo ter). Testa localmente antes
  de expores o servidor publicamente.
- Se mudares a password do intervals.icu ou quiseres cortar o acesso,
  revoga a API key em **Settings → Developer Settings** a qualquer momento.
