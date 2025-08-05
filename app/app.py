import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import tempfile
import os

# ======= CONFIGURAÇÕES DE PONTUAÇÃO =======

pontuacao_experiencia = {
    "0 a 1 ano": 2,
    "2 a 3 anos": 5,
    "3 a 6 anos": 8,
    "6 a 10 anos": 10,
    "+10 anos": 12,
}

pontuacao_formacao = {
    "mestrado": 8,
    "doutorado": 12
}

# Pontuação mínima exigida
META_PONTOS = 15

# ======= FUNÇÕES =======

def extrair_texto_arquivo(uploaded_file):
    nome = uploaded_file.name
    extensao = nome.lower().split('.')[-1]

    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + extensao) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    texto = ""
    try:
        if extensao == 'pdf':
            reader = PdfReader(tmp_path)
            texto = "\n".join([page.extract_text() or '' for page in reader.pages])
        elif extensao == 'docx':
            doc = Document(tmp_path)
            texto = "\n".join(p.text for p in doc.paragraphs)
        elif extensao == 'txt':
            with open(tmp_path, 'r', encoding='utf-8') as f:
                texto = f.read()
    finally:
        os.unlink(tmp_path)  # Remove o arquivo temporário

    return texto.lower()

def analisar_curriculo(texto):
    pontuacao = 0
    detalhes = []

    # Verifica experiência
    for faixa, pontos in pontuacao_experiencia.items():
        if faixa in texto:
            pontuacao += pontos
            detalhes.append({
                "categoria": "Experiência",
                "valor": faixa,
                "pontos": pontos
            })
            break  # Assume apenas uma faixa por currículo

    # Verifica formação
    for grau, pontos in pontuacao_formacao.items():
        if grau in texto:
            pontuacao += pontos
            detalhes.append({
                "categoria": "Formação",
                "valor": grau.title(),
                "pontos": pontos
            })

    return pontuacao, detalhes

# ======= STREAMLIT UI =======

st.set_page_config(page_title="Analisador de Currículos")
st.title("📄 Avaliador de Currículos — Experiência e Formação")
st.write("Faça upload de currículos com formato padrão e veja quais atingem a meta de pontuação.")

meta = st.slider("Pontuação mínima (meta)", min_value=5, max_value=30, value=META_PONTOS)

uploaded_files = st.file_uploader("🖇️ Envie os currículos aqui (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"], accept_multiple_files=True)

if uploaded_files:
    st.info(f"Avaliando {len(uploaded_files)} currículo(s)...")
    aprovados = []

    for arquivo in uploaded_files:
        texto = extrair_texto_arquivo(arquivo)
        pontuacao, detalhes = analisar_curriculo(texto)

        if pontuacao >= meta:
            aprovados.append({
                'nome': arquivo.name,
                'pontuacao': pontuacao,
                'detalhes': detalhes
            })

    if aprovados:
        st.success(f"✅ {len(aprovados)} currículo(s) aprovado(s):")
        for curriculo in aprovados:
            with st.expander(f"📌 {curriculo['nome']} — {curriculo['pontuacao']} pontos"):
                st.markdown("**Detalhamento:**")
                for item in curriculo['detalhes']:
                    st.markdown(f"- **{item['categoria']}**: {item['valor']} → {item['pontos']} ponto(s)")
    else:
        st.warning("⚠️ Nenhum currículo atingiu a meta de pontuação.")
