import fitz  # PyMuPDF
import re
import pandas as pd
import argparse
import os
import difflib

def extract_text_from_pdf(pdf_path):
    print(f"Lendo PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    pages = []
    for i in range(len(doc)):
        pages.append(doc[i].get_text("text"))
    return pages

def find_references_section(pages):
    body_pages = []
    ref_text = ""
    ref_start_page = -1
    match_obj = None
    
    # 1. Busca linha que inicie com REFERÊNCIAS de trás para frente (evita Sumário)
    pattern_strict = re.compile(
        r'^\s*(?:\d+[\.\s]*)?REFER[ÊE]NCIAS(?:\s+BIBLIOGR[ÁA]FICAS)?\b.*$',
        re.MULTILINE | re.IGNORECASE
    )
    
    for i in range(len(pages) - 1, -1, -1):
        page_text = pages[i]
        match = pattern_strict.search(page_text)
        if match:
            ref_start_page = i
            match_obj = match
            break

    # 2. Fallback: Se não encontrou linha exata, busca nas últimas 30% páginas por "REFERÊNCIAS" isolado
    if ref_start_page == -1:
        start_search_idx = max(0, int(len(pages) * 0.7))
        pattern_fallback = re.compile(
            r'\bREFER[ÊE]NCIAS(?:\s+BIBLIOGR[ÁA]FICAS)?\b',
            re.IGNORECASE
        )
        for i in range(len(pages) - 1, start_search_idx - 1, -1):
            page_text = pages[i]
            match = pattern_fallback.search(page_text)
            if match:
                ref_start_page = i
                match_obj = match
                break
            
    if ref_start_page != -1:
        for i in range(ref_start_page):
            body_pages.append(pages[i])
            
        page_text = pages[ref_start_page]
        body_pages.append(page_text[:match_obj.start()])
        ref_text += page_text[match_obj.end():] + "\n"
        
        for i in range(ref_start_page + 1, len(pages)):
            ref_text += pages[i] + "\n"
            
        # Ignora tudo que vier após ANEXO ou APÊNDICE
        end_match = re.search(
            r'^\s*(?:\d+[\.\s]*)?(ANEXO|APÊNDICE|APENDICE)S?\b.*$',
            ref_text,
            re.MULTILINE | re.IGNORECASE
        )
        if end_match:
            ref_text = ref_text[:end_match.start()]
    else:
        body_pages = pages
        ref_text = ""
            
    return body_pages, ref_text

def parse_references(ref_text):
    if not ref_text.strip():
        return []
        
    # Tenta separar por linhas duplas / parágrafos
    raw_refs = re.split(r'\n\s*\n', ref_text)
    refs = []
    for r in raw_refs:
        r = r.strip().replace('\n', ' ')
        if len(r) > 15:
            refs.append(r)
            
    # Se gerou pouquíssimas referências muito longas, usa fallback dividindo por padrão ABNT de autor
    if len(refs) <= 2 and len(ref_text) > 300:
        abnt_split = re.split(r'\n(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}(?:[,\s]|\s+[A-ZÀ-Ú]))', ref_text)
        refs = []
        for r in abnt_split:
            r = r.strip().replace('\n', ' ')
            if len(r) > 15:
                refs.append(r)

    return refs

def find_citations_in_body(body_pages):
    citations = []
    
    # Citações entre parênteses: (AUTOR, 2020), (AUTOR 1; AUTOR 2, 2020), (SILBERCHATZ, KORTH E SUDARSHAN, 2006)
    pattern_paren = re.compile(
        r'\(\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ\s,;&\-]+?)(?:\s+et\s+al\.)?\s*,\s*(\d{4})[a-z]?(?:\s*,\s*p\.\s*\d+|\s*,\s*\d+|\s*:\s*\d+)?\s*\)'
    )
    
    # Citações no texto: Autor (2020), Booch, Rumbaugh e Jacobson (2005), Pádua Filho (2003)
    pattern_text = re.compile(
        r'\b([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zà-úâêôãõç]+(?:\s+(?:Filho|Neto|Júnior|Sobrinho))?'
        r'(?:\s*,\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zà-úâêôãõç]+(?:\s+(?:Filho|Neto|Júnior|Sobrinho))?)*'
        r'(?:\s+e\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zà-úâêôãõç]+(?:\s+(?:Filho|Neto|Júnior|Sobrinho))?|\s+et\s+al\.)?)'
        r'\s*\(\s*(\d{4})[a-z]?(?::\s*\d+|,\s*p\.\s*\d+|\s+p\.\s*\d+)?\s*\)'
    )
    
    ignorar = [
        "AUTOR", "AUTORES", "AUTORAL", "O AUTOR", "OS AUTORES", "A AUTORA", "AS AUTORAS",
        "PRÓPRIO AUTOR", "PRÓPRIOS AUTORES", "PRÓPRIA AUTORA", "PRÓPRIAS AUTORAS",
        "DO AUTOR", "DOS AUTORES", "DA AUTORA", "DAS AUTORAS",
        "ELABORADO PELO AUTOR", "ELABORADA PELO AUTOR", "FONTE"
    ]
    
    for page_num, text in enumerate(body_pages, start=1):
        # 1. Citações parentéticas
        for match in pattern_paren.finditer(text):
            autor = match.group(1).strip()
            if autor.upper() in ignorar:
                continue
                
            ano = match.group(2).strip()
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            contexto = text[start:end].replace('\n', ' ')
            
            citations.append({
                'tipo': 'Parenteses',
                'autor': autor,
                'ano': ano,
                'pagina': page_num,
                'contexto': f"...{contexto}...",
                'citacao_completa': match.group(0)
            })
            
        # 2. Citações no texto
        for match in pattern_text.finditer(text):
            autor = match.group(1).strip()
            if autor.upper() in ignorar:
                continue
                
            ano = match.group(2).strip()
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            contexto = text[start:end].replace('\n', ' ')
            
            citations.append({
                'tipo': 'Texto',
                'autor': autor,
                'ano': ano,
                'pagina': page_num,
                'contexto': f"...{contexto}...",
                'citacao_completa': match.group(0)
            })
            
    return citations

def extract_author_tokens(autor_str):
    """Extrai os sobrenomes/tokens principais do autor citado."""
    clean = re.sub(r'\b(e|et\s+al\.|and)\b', ' ', autor_str, flags=re.IGNORECASE)
    parts = re.split(r'[;,\s]+', clean)
    stop_words = {'filho', 'neto', 'junior', 'júnior', 'sobrinho', 'dos', 'das', 'del', 'von', 'van', 'der', 'de', 'da', 'do'}
    tokens = [p.strip().upper() for p in parts if len(p.strip()) > 2 and p.strip().lower() not in stop_words]
    return tokens

def is_author_match(citation_author, ref_text):
    ref_upper = ref_text.upper()
    tokens = extract_author_tokens(citation_author)
    if not tokens:
        return False
        
    for token in tokens:
        # Correspondência exata de substring
        if token in ref_upper:
            return True
            
        # Correspondência por similaridade (fuzzy) contra palavras da referência
        ref_words = re.findall(r'[A-ZÀ-Ú]{3,}', ref_upper)
        for w in ref_words:
            ratio = difflib.SequenceMatcher(None, token, w).ratio()
            if ratio >= 0.8:  # tolera pequenos erros de digitação como Silberchatz/Silberschatz, Pressman/Presmann
                return True
    return False

def match_citations(citations, references):
    results = []
    used_refs = set()
    
    for cit in citations:
        ano_key = cit['ano']
        found_ref = None
        year_mismatch_ref = None
        
        # 1. Busca por correspondência de autor e ano exato
        for i, ref in enumerate(references):
            if is_author_match(cit['autor'], ref):
                if ano_key in ref:
                    found_ref = ref
                    used_refs.add(i)
                    break
                elif year_mismatch_ref is None:
                    year_mismatch_ref = ref
                
        if found_ref:
            status = '✅ OK'
            ref_final = found_ref
        elif year_mismatch_ref:
            status = '⚠️ ANO DIVERGENTE'
            ref_final = f"[Ano divergente em relação à ref]: {year_mismatch_ref}"
        else:
            status = '❌ FALTA NA BIBLIOGRAFIA'
            ref_final = 'NÃO ENCONTRADA'
            
        results.append({
            'Status': status,
            'Citação Encontrada': cit['citacao_completa'],
            'Página': cit['pagina'],
            'Contexto': cit['contexto'],
            'Referência Correspondente': ref_final
        })
        
    # Identifica referências não utilizadas no corpo
    for i, ref in enumerate(references):
        if i not in used_refs:
            results.append({
                'Status': 'ℹ️ SOBRANDO (NÃO CITADA)',
                'Citação Encontrada': '-',
                'Página': '-',
                'Contexto': '-',
                'Referência Correspondente': ref
            })
            
    return results

def run_validation(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Erro: Arquivo '{pdf_path}' não encontrado.")
        return []

    print("Iniciando extração do PDF...")
    pages = extract_text_from_pdf(pdf_path)
    
    print("Separando texto e referências...")
    body_pages, ref_text = find_references_section(pages)
    
    if not ref_text.strip():
        print("Aviso: Seção de referências não encontrada automaticamente. Verifique o cabeçalho 'REFERÊNCIAS BIBLIOGRÁFICAS'.")
        
    print("Mapeando lista de referências...")
    references = parse_references(ref_text)
    print(f"{len(references)} referências encontradas.")
    
    print("Buscando citações no corpo do texto...")
    citations = find_citations_in_body(body_pages)
    print(f"{len(citations)} citações encontradas.")
    
    print("Cruzando dados...")
    results = match_citations(citations, references)
    return results

def main():
    parser = argparse.ArgumentParser(description="Validador de Citações ABNT em TCCs")
    parser.add_argument("pdf_path", help="Caminho para o arquivo PDF do TCC")
    parser.add_argument("--output", default="relatorio_citacoes.xlsx", help="Caminho do arquivo Excel de saída")
    args = parser.parse_args()
    
    results = run_validation(args.pdf_path)
    if not results:
        return
        
    print(f"Gerando relatório: {args.output}")
    df = pd.DataFrame(results)
    
    try:
        df.to_excel(args.output, index=False)
        print("Relatório Excel gerado com sucesso!")
    except ImportError:
        csv_out = args.output.replace('.xlsx', '.csv')
        df.to_csv(csv_out, index=False, sep=';', encoding='utf-8-sig')
        print(f"Módulo openpyxl não encontrado. Relatório gerado como CSV: {csv_out}")

if __name__ == "__main__":
    main()

