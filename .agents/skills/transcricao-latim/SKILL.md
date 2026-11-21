---
name: transcricao-latim
description: >-
  Transcreve páginas digitalizadas de livros antigos em latim em lotes pequenos
  (máx. 4 páginas por execução) para economia de tokens, mantendo estado em JSON
  e consolidando capítulos completos em Markdown. Use quando o usuário pedir
  para transcrever, processar lote de páginas, ou continuar a transcrição de
  latim (Orlandini).
---

# Workflow: Transcrição Incremental de Latim (Orlandini)

## Parâmetros de Controle de Tokens
- **Lote máximo por execução (`BATCH_SIZE`):** `4` páginas. Nunca processe mais de 4 imagens em uma única chamada deste workflow.
- **Processamento isolado:** Ao ler uma imagem, processe-a, salve imediatamente seu arquivo em `output_paginas/` e não carregue imagens anteriores no contexto.

## Estrutura de Arquivos do Projeto
- `input_paginas/`: Imagens ordenadas sequencialmente (`001.jpg`, `002.jpg`, `003.jpg`...).
- `output_paginas/`: Transcrições individuais por página (`pag_001.md`, `pag_002.md`...).
- `output_capitulos/`: Capítulos fechados, costurados e divididos em grandes parágrafos (`cap_01.md`, `cap_02.md`...).
- `estado_transcricao.json`: Controle de progresso para retomada sem releitura.
- `log_duvidas.md`: Registro cumulativo de palavras marcadas com `[palavra?]`.

---

## Etapa 0: Verificação de Estado (Leitura Mínima)

1. Verifique se `estado_transcricao.json` existe na raiz. Se não existir, crie-o com:
   ```json
   {
     "ultima_pagina_processada": null,
     "capitulos_concluidos": [],
     "capitulo_em_aberto": null
   }
   ```
2. Identifique as próximas páginas em `input_paginas/` após `ultima_pagina_processada` (limitado ao máximo de 4 páginas no lote atual).

---

## Etapa 1: Leitura Individual via OCR e Normalização Tipográfica

Processe **uma imagem por vez** da pasta `input_paginas/`, seguindo a ordem numérica exata dos arquivos. Para cada página, aplique rigorosamente as regras abaixo e salve o resultado temporário em `output_paginas/pag_XXX.md`:

### Regras de Transcrição e Normalização
1. **Exclusão de Elementos Periféricos:**
   - Ignore títulos correntes no topo da página (ex.: *LIBER POSTERIOR*, *PETRI FABRI VITA*) e números de página.
   - Ignore notas marginais cortadas ou completas nas bordas esquerda/direita.
   - Identifique e isole a **palavra de reclamo (*custos*)** no canto inferior direito (a palavra solta abaixo da última linha que antecipa a primeira palavra da página seguinte). Não a duplique ao unir as páginas.
2. **Conversão de Caracteres Históricos:**
   - Converta todo `ſ` (s longo) para `s` moderno (ex.: `ſancti` → `sancti`, `eſſe` → `esse`). Atenção para não confundir `ſ` com `f` (ex.: distinguir `semina` de `femina`, `sinebat` de `finebat`, `fuisse` de `suisse`).
   - Padronize `u` e `v` conforme o valor fonético/gramatical (ex.: `vt` → `ut`, `diuina` → `divina`, `CAPVT` → `CAPUT`, `Vnicus` → `Unicus`).
   - Padronize `i` e `j` nos encontros vocálicos finais/mediais (ex.: `Ignatij` → `Ignatii`, `Pariſijs` → `Parisiis`, `ijſdem` → `iisdem`).
   - Expanda os ditongos ligados `æ` e `œ` para `ae` e `oe` (ex.: `præcepti` → `praecepti`, `cœpit` → `coepit`).
   - Remova acentos graves, agudos e circunflexos tipográficos típicos do latim neolatino (ex.: `verò` → `vero`, `à` → `a`, `maximè` → `maxime`, `penitùs` → `penitus`).
3. **Expansão de Abreviações:**
   - Expanda o símbolo enclítico `q;` para `que` (ex.: `ſuſtentariq;` → `sustentarique`, `adeoq;` → `adeoque`).
   - Expanda todos os tildes de nasalização (`˜`) sobre vogais para `m` ou `n` conforme a morfologia latina (ex.: `cõmentariis` → `commentariis`, `mentẽ` → `mentem`, `quædã` → `quaedam`, `Põtificis` → `Pontificis`).
   - Mantenha abreviações nominais consagradas apenas se forem títulos/prenomes padrão (ex.: `D.` para *Divus*, `B.` para *Beatus*), mas expanda abreviações de desinência como `hominib.` → `hominibus` e `reip.` → `reip.` (ou `reipublicae` se não houver ambiguidade).
4. **Protocolo de Dúvida e Auditoria (`[palavra?]`):**
   - Se uma palavra estiver borrada, cortada na encadernação, contiver erro tipográfico evidente da edição antiga (ex.: `deſtituſi` em vez de `destituti`, `vieos` em vez de `vicos`) ou gerar dúvida sintática/morfológica, transcreva a forma provável entre colchetes com interrogação: `[destituti?]`.
   - Registre cada ocorrência no arquivo `log_duvidas.md` indicando o número da página, a forma impressa no original, a forma sugerida e a justificativa gramatical.

---

## Etapa 2: Costura de Quebras de Página e Agrupamento por Capítulo

Após transcrever todas as páginas do lote, una o texto sequencialmente para reconstruir o fluxo contínuo da obra:

1. **Resolução de Hifenizações e Reclamos:**
   - Una palavras divididas por hífen no final de linha ou no final de página (ex.: `inſi-` no fim da p. X + `dentem` no início da p. Y → `insidentem`).
   - Verifique o reclamo (*custos*) do rodapé de cada página contra a primeira palavra da página seguinte, garantindo que nenhuma palavra seja omitida ou duplicada na transição.
2. **Detecção de Fronteiras de Capítulo:**
   - Identifique cada cabeçalho de capítulo (ex.: `CAPUT I.`, `CAPUT IIII.`, `CAPUT V.`) e seu respectivo sumário/subtítulo em itálico.
   - Separe o texto completo em arquivos individuais na pasta `output_capitulos/`, nomeados sequencialmente conforme a numeração do livro (ex.: `cap_01.md`, `cap_04.md`, `cap_05.md`).
   - Preserve no topo de cada arquivo o título e o subtítulo formatados em negrito:
     ```markdown
     **CAPUT V.**
     **Peregrinationes Fabri Parisiis Venetias inde Roma, ac Venetias rursum, & alia.**
     ```
3. **Deduplicação de Sobreposição de Captura:**
   - Antes de unir duas páginas consecutivas, verifique se as 1 ou 2 primeiras linhas da página atual são idênticas às 1 ou 2 últimas linhas da página anterior (comum em capturas de tela sequenciais). Se houver sobreposição, remova a duplicata na junção.
4. **Atualização de Estado:**
   - Atualize `estado_transcricao.json` com a `ultima_pagina_processada`, `capitulos_concluidos` e `capitulo_em_aberto`.

---

## Etapa 3: Divisão Retórica em Grandes Parágrafos

Para cada arquivo gerado ou atualizado em `output_capitulos/`, transforme o bloco único de texto corrido em **grandes parágrafos temáticos** (normalmente entre 3 e 6 parágrafos por capítulo, dependendo da extensão):

1. **Critérios de Segmentação:**
   - **Nunca quebre frases ao meio:** Todo parágrafo deve começar imediatamente após um ponto final (`.`), ponto de interrogação (`?`) ou dois-pontos que encerrem um período completo.
   - **Progressão Narrativa e Retórica:** Agrupe os períodos por unidades de sentido claras (ex.: *contexto/cenário inicial → ação principal ou deslocamento → consequência espiritual/moral ou ensinamento patrístico*).
   - **Marcadores Discursivos Latinos:** Utilize transições clássicas como pontos naturais de abertura de parágrafo quando introduzirem uma nova etapa da narrativa (ex.: *Deinde*, *Itaque*, *Verum*, *Eodem anno*, *Quid de... dicam*, *Sed ad tuendum...*, *Denique*).
2. **Integridade Textual:**
   - Não altere, resuma, parafraseie ou omita nenhuma palavra do texto latino estabelecido na Etapa 2.
   - Mantenha todas as marcações `[palavra?]` intactas dentro dos parágrafos para sua revisão visual final.

---

## Etapa 4: Entrega e Checklist Final

Ao concluir a execução do lote de páginas, apresente um relatório sucinto contendo:
1. Páginas processadas no lote atual e estado atualizado em `estado_transcricao.json`.
2. Lista dos arquivos de capítulos criados ou atualizados em `output_capitulos/` com a contagem de parágrafos de cada um.
3. Resumo das entradas adicionadas ao `log_duvidas.md` que exigem sua conferência visual direta nas imagens originais.

