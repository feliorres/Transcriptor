#!/usr/bin/env python3
"""
Extrai um lote de páginas do arquivo input_paginas/texto_original.pdf
em arquivos PDF individuais de 1 página em input_paginas/lote_atual/,
permitindo a leitura visual em alta resolução sem estourar o limite de tokens.

Uso:
  python3 .agents/skills/transcricao-latim/scripts/extrair_lote_pdf.py --livro 17 20
  python3 .agents/skills/transcricao-latim/scripts/extrair_lote_pdf.py --pdf 37 40
"""
import argparse
import os
import sys
import pypdf

PDF_PATH = "input_paginas/texto_original.pdf"
OUT_DIR = "input_paginas/lote_atual"
OFFSET_LIVRO_PARA_PDF = 20  # pág. 1 do livro = pág. 21 do PDF (1 + 20)


def main():
    parser = argparse.ArgumentParser(description="Extrai lote de até 4 páginas do PDF original.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--livro",
        nargs=2,
        type=int,
        metavar=("INICIO", "FIM"),
        help="Intervalo de páginas pela numeração impressa do livro (ex.: 17 20)",
    )
    group.add_argument(
        "--pdf",
        nargs=2,
        type=int,
        metavar=("INICIO", "FIM"),
        help="Intervalo de páginas pela numeração do arquivo PDF 1-based (ex.: 37 40)",
    )
    args = parser.parse_args()

    if not os.path.exists(PDF_PATH):
        print(f"Erro: Arquivo {PDF_PATH} não encontrado.", file=sys.stderr)
        sys.exit(1)

    if args.livro:
        p_ini, p_fim = args.livro
        pdf_ini = p_ini + OFFSET_LIVRO_PARA_PDF
        pdf_fim = p_fim + OFFSET_LIVRO_PARA_PDF
    else:
        pdf_ini, pdf_fim = args.pdf
        p_ini = pdf_ini - OFFSET_LIVRO_PARA_PDF
        p_fim = pdf_fim - OFFSET_LIVRO_PARA_PDF

    qtd = pdf_fim - pdf_ini + 1
    if qtd < 1 or qtd > 4:
        print(f"Erro: O lote deve conter entre 1 e 4 páginas (solicitado: {qtd}).", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    for f in os.listdir(OUT_DIR):
        if f.endswith(".pdf"):
            os.remove(os.path.join(OUT_DIR, f))

    reader = pypdf.PdfReader(PDF_PATH)
    total = len(reader.pages)

    arquivos_gerados = []
    for pdf_pag in range(pdf_ini, pdf_fim + 1):
        idx = pdf_pag - 1
        if idx < 0 or idx >= total:
            print(f"Erro: Página PDF {pdf_pag} fora do limite (1..{total}).", file=sys.stderr)
            sys.exit(1)

        pag_livro = pdf_pag - OFFSET_LIVRO_PARA_PDF
        if pag_livro >= 1:
            nome_arq = f"pag_{pag_livro:03d}_pdf{pdf_pag:03d}.pdf"
        else:
            nome_arq = f"pre_{pdf_pag:03d}.pdf"

        caminho_saida = os.path.join(OUT_DIR, nome_arq)
        writer = pypdf.PdfWriter()
        writer.add_page(reader.pages[idx])
        with open(caminho_saida, "wb") as f_out:
            writer.write(f_out)
        arquivos_gerados.append((pag_livro, pdf_pag, caminho_saida))

    print(f"Lote extraído com sucesso ({len(arquivos_gerados)} página(s)):")
    for pag_livro, pdf_pag, caminho in arquivos_gerados:
        label_livro = f"Livro p. {pag_livro}" if pag_livro >= 1 else "Preliminar"
        print(f"  - {label_livro} (PDF p. {pdf_pag}) -> {caminho}")


if __name__ == "__main__":
    main()

