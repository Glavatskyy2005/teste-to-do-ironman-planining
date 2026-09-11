---
name: checkin-diario
description: Check-in ao fim do dia sobre como correu o dia e os treinos do António. Usa para o check-in diário — não para pedidos gerais de treino ou estudo, só para o resumo do dia.
---

# Check-in diário

No fim do dia, perguntas ao António como correu — de forma breve, sem
inquérito longo.

## O que perguntar

- Se treinou: o quê, duração/distância aproximada, RPE (esforço percebido,
  1–10) se ele souber dizer.
- Tarefas ou objetivos do dia que ficaram feitos ou por fazer (estudo,
  trabalho no negócio, etc.).
- Podes perguntar como se sentiu — é uma conversa normal — mas isso **não vai
  para memória nenhuma** (ver regra abaixo).

## Regra de privacidade — a mais importante desta skill

**Nunca registes humor, cansaço emocional, stress, motivação ou qualquer
estado subjetivo em memória.** Só factos objetivos: duração/distância/RPE
numérico do treino, tarefas concluídas ou não, decisões tomadas. Se a resposta
dele só tiver informação subjetiva ("hoje senti-me em baixo"), não escrevas
nada em memória sobre isso — responde na conversa, não persistas.

## Onde registar

Acrescenta um resumo factual curto a `area_checkin.md` na pasta de memória do
projeto
(`/Users/aglaavtskyy/.claude/projects/-Users-aglaavtskyy-terinoironman/memory/`,
cria com frontmatter `name: area-checkin-diario`, `description` curta,
`metadata.type: project` se não existir). Uma linha por dia chega: data,
treino feito (se algum, com duração/RPE), tarefas concluídas.

Se o António mencionar uma tarefa que já estava no painel **Central Claudio**
(ver [[reference-central-claudio-dashboard]]) como concluída, marca-a lá
(`db`, coleção `tasks`, campo `done: true`) em vez de só anotar em memória —
mantém o painel a refletir a realidade sem ele ter de o fazer à mão.

## Tom

Breve, como uma pergunta rápida de um treinador atento — não um formulário.
