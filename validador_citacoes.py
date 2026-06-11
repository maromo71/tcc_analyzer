import fitz  # PyMuPDF
import re
import pandas as pd
import argparse
import os

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
    
    # Busca de trás para frente para evitar pegar o Sumário
    for i in range(len(pages)-1, -1, -1):
        page_text = pages[i]
        match = re.search(r'^\s*REFER[ÊE]NCIAS(?:\s+BIBLIOGR[ÁA]FICAS)?\s*$', page_text, re.MULTILINE | re.IGNORECASE)
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
        end_match = re.search(r'^\s*(ANEXO|APÊNDICE|APENDICE)S?\b.*$', ref_text, re.MULTILINE | re.IGNORECASE)
        if end_match:
            ref_text = ref_text[:end_match.start()]
    else:
        body_pages = pages
        ref_text = ""
            
    return body_pages, ref_text

def parse_references(ref_text):
    # Separa por linhas duplas ou parágrafos
    raw_refs = re.split(r'\n\s*\n', ref_text)
    refs = []
    for r in raw_refs:
        r = r.strip().replace('\n', ' ')
        if len(r) > 15: # Filtra ruídos
            refs.append(r)
    return refs

def find_citations_in_body(body_pages):
    citations = []
    # Padrão 1: (AUTOR, Ano) ou (AUTOR; AUTOR, Ano) ou (AUTOR et al., Ano)
    pattern1 = re.compile(r'\(([A-ZÀ-Úa-z\s]+(?:;\s*[A-ZÀ-Úa-z\s]+)*)(?:\s+et\s+al\.)?(?:.+?)?,\s*(\d{4})(?:.*?)\)')
    
    # Padrão 2: Autor (Ano) ou Autor et al. (Ano)
    pattern2 = re.compile(r'([A-Z][a-zÀ-ú]+(?:\s+e\s+[A-Z][a-zÀ-ú]+|\s+et\s+al\.)?)\s+\((\d{4})(?:.*?)\)')
    
    for page_num, text in enumerate(body_pages, start=1):
        # Encontra padrão 1
        for match in pattern1.finditer(text):
            autor = match.group(1).strip()
            
            # Ignora citações de autoria própria para imagens e tabelas
            ignorar = ["AUTOR", "AUTORES", "AUTORAL", "O AUTOR", "OS AUTORES", "A AUTORA", "AS AUTORAS", "PRÓPRIO AUTOR", "PRÓPRIOS AUTORES", "PRÓPRIA AUTORA", "PRÓPRIAS AUTORAS", "DO AUTOR", "DOS AUTORES", "DA AUTORA", "DAS AUTORAS"]
            if autor.upper() in ignorar:
                continue
                
            ano = match.group(2).strip()
            
            # Pega um trecho ao redor para contexto
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
            
        # Encontra padrão 2
        for match in pattern2.finditer(text):
            autor = match.group(1).strip()
            
            # Ignora citações de autoria própria
            ignorar = ["AUTOR", "AUTORES", "AUTORAL", "O AUTOR", "OS AUTORES", "A AUTORA", "AS AUTORAS", "PRÓPRIO AUTOR", "PRÓPRIOS AUTORES", "PRÓPRIA AUTORA", "PRÓPRIAS AUTORAS", "DO AUTOR", "DOS AUTORES", "DA AUTORA", "DAS AUTORAS"]
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

def match_citations(citations, references):
    results = []
    used_refs = set()
    
    for cit in citations:
        autor_key = cit['autor'].split(';')[0].split(',')[0].split(' ')[0].upper()
        ano_key = cit['ano']
        
        found_ref = None
        for i, ref in enumerate(references):
            if autor_key in ref.upper() and ano_key in ref:
                found_ref = ref
                used_refs.add(i)
                break
                
        if found_ref:
            status = '✅ OK'
        else:
            status = '❌ FALTA NA BIBLIOGRAFIA'
            
        results.append({
            'Status': status,
            'Citação Encontrada': cit['citacao_completa'],
            'Página': cit['pagina'],
            'Contexto': cit['contexto'],
            'Referência Correspondente': found_ref if found_ref else 'NÃO ENCONTRADA'
        })
        
    # Identifica referências não utilizadas
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
        print("Aviso: Seção de referências não encontrada automaticamente. Verifique se o título é exatamente 'REFERÊNCIAS BIBLIOGRÁFICAS'.")
        
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
    
    # Salva em Excel se openpyxl estiver instalado, senão salva em CSV
    try:
        df.to_excel(args.output, index=False)
        print("Relatório Excel gerado com sucesso!")
    except ImportError:
        csv_out = args.output.replace('.xlsx', '.csv')
        df.to_csv(csv_out, index=False, sep=';', encoding='utf-8-sig')
        print(f"Módulo openpyxl não encontrado. Relatório gerado como CSV: {csv_out}")

if __name__ == "__main__":
    main()
