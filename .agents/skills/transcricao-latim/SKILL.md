---
name: transcricao-latim
description: >-
  Transcreve páginas digitalizadas de livros antigos em latim a partir do PDF
  original (input_paginas/texto_original.pdf) em lotes pequenos (máx. 4 páginas
  por execução) para economia de tokens, mantendo estado em JSON e consolidando
  capítulos completos em Markdown. Use quando o usuário pedir para transcrever,
  processar lote de páginas ou capítulos, ou continuar a transcrição de latim
  (Orlandini - Vitae Petri Fabri).
---

# Workflow: Transcrição Incremental de Latim (Orlandini — *Vitae Petri Fabri*)

## Fonte Principal e Mapeamento de Páginas
- **Arquivo Fonte:** `input_paginas/texto_original.pdf` (322 páginas no PDF).
- **Correspondência Livro ↔ PDF (`OFFSET = +20`):**
  - Páginas preliminares (Folha de rosto, Epístola dedicatória, Proêmio, Aprovação): Páginas do PDF `7` a `20`.
  - **Página `1` do Livro (*Liber Prior, Caput I*)** = **Página `21` do PDF**.
  - Fórmula geral: **`Página_PDF = Página_Livro + 20`** (ex.: Página `17` do livro = Página `37` do PDF).
  - *Index Capitum* original no PDF: Páginas `312` a `315` do PDF.

## Parâmetros de Controle de Tokens
- **Lote máximo por execução (`BATCH_SIZE`):** `4` páginas. Nunca processe mais de 4 páginas do PDF em uma única chamada deste workflow.
- **Extração Cirúrgica de Páginas:** Nunca carregue `input_paginas/texto_original.pdf` inteiro de uma vez. Utilize sempre o script auxiliar `.agents/skills/transcricao-latim/scripts/extrair_lote_pdf.py` para extrair apenas as páginas do lote atual (1 página por PDF temporário em `input_paginas/lote_atual/`) e leia um arquivo por vez com `read_file`.
- **Processamento isolado:** Ao ler a página extraída, processe-a visualmente (ignorando erros do OCR bruto embutido no Google Books), salve imediatamente seu arquivo em `output_paginas/pag_XXX.md` e passe para a seguinte.

## Estrutura de Arquivos do Projeto
- `input_paginas/texto_original.pdf`: PDF completo da edição histórica (*Vitae Petri Fabri*, Lyon, 1617).
- `input_paginas/lote_atual/`: Pasta temporária (ignorada no Git) onde o script extrai as 1–4 páginas do lote ativo para leitura em alta resolução.
- `output_paginas/`: Transcrições individuais por página do livro (`pag_001.md`, `pag_002.md`...).
- `output_capitulos/liber_prior/` e `output_capitulos/liber_posterior/`: Capítulos fechados, costurados e divididos em grandes parágrafos (`cap_01.md`, `cap_02.md`...).
- `INDEX_CAPITUM.md`: Índice geral com mapeamento de capítulos, páginas do livro, páginas do PDF e status.
- `estado_transcricao.json`: Controle de progresso para retomada sem releitura.
- `log_duvidas.md`: Registro cumulativo de palavras marcadas com `[palavra?]`.

---

## Etapa 0: Verificação de Estado e Extração do Lote

1. Leia `estado_transcricao.json` e `INDEX_CAPITUM.md` para identificar quais páginas do livro (ou qual capítulo) devem ser processadas a seguir.
2. Extraia o lote de no máximo 4 páginas do PDF original executando o script:
   ```bash
   python3 .agents/skills/transcricao-latim/scripts/extrair_lote_pdf.py --livro <PAG_INICIO> <PAG_FIM>
   ```
   *(Ou `--pdf <PDF_INICIO> <PDF_FIM>` caso esteja transcrevendo as páginas preliminares antes da página 1 do livro).*

---

## Etapa 1: Leitura Individual em Alta Resolução e Normalização Tipográfica

Use `read_file` em **um arquivo PDF de página única por vez** dentro de `input_paginas/lote_atual/`. Inspecione a imagem renderizada da página (não confie cegamente na camada de OCR antigo do Google Books, pois ela troca `ſ` por `f` e corrompe ligaturas). Para cada página, aplique rigorosamente as regras abaixo e salve em `output_paginas/pag_XXX.md`:

### Regras de Transcrição e Normalização
1. **Exclusão de Elementos Periféricos:**
   - Ignore títulos correntes no topo da página (ex.: *LIBER PRIOR*, *LIBER POSTERIOR*, *PETRI FABRI VITAE*) e números de página.
   - Ignore notas marginais impressas nas bordas esquerda/direita e assinaturas de caderno no rodapé (ex.: `A`, `B`, `T 3`, *Digitized by Google*).
   - Identifique e isole a **palavra de reclamo (*custos*)** no canto inferior direito (a palavra solta abaixo da última linha que antecipa a primeira palavra da página seguinte). Não a duplique ao unir as páginas.
2. **Conversão de Caracteres Históricos:**
   - Converta todo `ſ` (s longo) para `s` moderno (ex.: `ſancti` → `sancti`, `eſſe` → `esse`). Atenção para não confundir `ſ` com `f` (ex.: distinguir `semina` de `femina`, `sinebat` de `finebat`, `fuisse` de `suisse`).
   - Padronize `u` e `v` conforme o valor fonético/gramatical (ex.: `vt` → `ut`, `diuina` → `divina`, `CAPVT` → `CAPUT`, `Vnicus` → `Unicus`).
   - Padronize `i` e `j` nos encontros vocálicos finais/mediais (ex.: `Ignatij` → `Ignatii`, `Pariſijs` → `Parisiis`, `ijſdem` → `iisdem`).
   - Expanda os ditongos ligados `æ` e `œ` para `ae` e `oe` (ex.: `præcepti` → `praecepti`, `cœpit` → `coepit`).
   - Remova acentos graves, agudos, circunflexos e tremas tipográficos típicos do latim neolatino (ex.: `verò` → `vero`, `à` → `a`, `maximè` → `maxime`, `penitùs` → `penitus`, `poëtas` → `poetas`, `coëgit` → `coegit`).
3. **Expansão de Abreviações:**
   - Expanda o símbolo enclítico `q;` para `que` (ex.: `ſuſtentariq;` → `sustentarique`, `adeoq;` → `adeoque`).
   - Expanda todos os tildes de nasalização (`˜`) sobre vogais para `m` ou `n` conforme a morfologia latina (ex.: `cõmentariis` → `commentariis`, `mentẽ` → `mentem`, `quædã` → `quaedam`, `Põtificis` → `Pontificis`).
   - Mantenha abreviações nominais consagradas apenas se forem títulos/prenomes padrão (ex.: `D.` para *Divus*, `B.` para *Beatus*), mas expanda abreviações de desinência como `hominib.` → `hominibus` e `reip.` → `reip.` (ou `reipublicae` se não houver ambiguidade).
4. **Protocolo de Dúvida e Auditoria (`[palavra?]`):**
   - Se uma palavra estiver borrada, cortada na encadernação, contiver erro tipográfico evidente da edição antiga (ex.: `deſtituſi` em vez de `destituti`, `vieos` em vez de `vicos`, `exercerdum` em vez de `exercendum`) ou gerar dúvida sintática/morfológica, transcreva a forma provável entre colchetes com interrogação: `[destituti?]`.
   - Registre cada ocorrência no arquivo `log_duvidas.md` indicando o número da página (livro e PDF), a forma impressa no original, a forma sugerida e a justificativa gramatical.

---

## Etapa 2: Costura de Quebras de Página e Agrupamento por Capítulo

Após transcrever todas as páginas do lote, una o texto sequencialmente para reconstruir o fluxo contínuo da obra:

1. **Resolução de Hifenizações e Reclamos:**
   - Una palavras divididas por hífen no final de linha ou no final de página (ex.: `inſi-` no fim da p. X + `dentem` no início da p. Y → `insidentem`).
   - Verifique o reclamo (*custos*) do rodapé de cada página contra a primeira palavra da página seguinte, garantindo que nenhuma palavra seja omitida ou duplicada na transição.
2. **Detecção de Fronteiras de Capítulo:**
   - Identifique cada cabeçalho de capítulo (ex.: `CAPUT I.`, `CAPUT IIII.`, `CAPUT V.`) e seu respectivo sumário/subtítulo em itálico, consultando `INDEX_CAPITUM.md`.
   - Separe o texto completo em arquivos individuais na pasta `output_capitulos/liber_prior/` ou `output_capitulos/liber_posterior/`, nomeados sequencialmente conforme a numeração do livro (ex.: `cap_01.md`, `cap_06.md`).
   - Preserve no topo de cada arquivo o título e o subtítulo formatados em negrito:
     ```markdown
     **CAPUT V.**
     **Peregrinationes Fabri Parisiis, Venetias inde Roma, ac Venetias rursum, & aliae.**
     ```
3. **Deduplicação de Sobreposição:**
   - Antes de unir duas páginas consecutivas, verifique se há qualquer linha repetida e remova duplicatas na junção.
4. **Atualização de Estado:**
   - Atualize `estado_transcricao.json` e `INDEX_CAPITUM.md` com a última página processada (livro e PDF), capítulos concluídos e capítulos em aberto.

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

Ao concluir a execução do lote de páginas, limpe os arquivos temporários de `input_paginas/lote_atual/` e apresente um relatório sucinto contendo:
1. Páginas processadas no lote atual (numeração do Livro e do PDF) e estado atualizado em `estado_transcricao.json`.
2. Lista dos arquivos de capítulos criados ou atualizados em `output_capitulos/` com a contagem de parágrafos de cada um.
3. Resumo das entradas adicionadas ao `log_duvidas.md` que exigem conferência visual direta.
