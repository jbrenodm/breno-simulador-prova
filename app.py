import streamlit as st
import random
import re
from datetime import datetime
from database import ExamRepository
from parser_engine import ExamParser
from report_gen import ExamReport

class ExamApp:
    def __init__(self):
        self.repo = ExamRepository()
        self._init_session_state()

    def _init_session_state(self):
        if 'questoes' not in st.session_state:
            st.session_state.update({
                'questoes': [], 'idx': 0, 'respostas': {}, 'finalizado': False
            })

    def run(self):
        st.title("🛡️ Simulador de Exame")
        
        if not st.session_state.questoes:
            self.render_setup()
        else:
            self.render_exam()

    def render_setup(self):
        # 1. Sidebar para carregar ou EXCLUIR exames
        exames = self.repo.get_all_exam_names()
        with st.sidebar:
            st.header("📂 Meus Simulados")
            if exames:
                escolha = st.selectbox("Selecione um simulado:", [""] + exames)
                if escolha:
                    dados = self.repo.load_exam(escolha)
                    
                    # Verificação de segurança para simulados vazios
                    if not dados:
                        st.warning("⚠️ Este simulado não possui questões. Tente reimportar o arquivo.")
                    else:
                        # O slider só aparece se houver questões (max_value >= 1)
                        qtd = st.slider(
                            "Quantidade de questões:", 
                            min_value=1, 
                            max_value=len(dados), 
                            value=min(len(dados), 10)
                        )
                        
                        if st.button("🚀 Iniciar Simulado", use_container_width=True):
                            st.session_state.questoes = random.sample(dados, qtd)
                            st.session_state.idx = 0
                            st.session_state.respostas = {}
                            st.session_state.finalizado = False
                            st.rerun()
                    
                    st.divider()
                    
                    # Funcionalidade de Exclusão com confirmação
                    st.warning("Zona de Perigo")
                    confirma = st.checkbox(f"Confirmar exclusão de '{escolha}'")
                    if st.button("🗑️ Excluir Exame", type="secondary", use_container_width=True, disabled=not confirma):
                        if self.repo.delete_exam(escolha):
                            st.success("Exame removido!")
                            st.rerun()
            else:
                st.info("Nenhum simulado salvo.")

        # 2. Área Central com Abas (Corrigido para evitar IndentationError)
        tab_import, tab_edit = st.tabs(["📥 Importar Novo", "✏️ Editar/Corrigir"])

        with tab_import:
            st.subheader("Importar via arquivo")
            nome_novo = st.text_input("Nome do Exame")
            file = st.file_uploader("TXT ou PDF", type=['txt', 'pdf'])
            
            if st.button("Salvar Novo Simulado", type="primary"):
                if nome_novo and file:
                    try:
                        if file.type == "application/pdf":
                            raw_text = ExamParser.extract_text_from_pdf(file.read())
                        else:
                            raw_text = file.getvalue().decode("utf-8")
                        
                        exam = ExamParser.parse_raw_text(nome_novo, raw_text)
                        if self.repo.save_exam(exam):
                            st.success(f"✅ Exame '{nome_novo}' salvo!")
                            st.rerun()
                        else:
                            st.error("❌ Erro: Nome já existe ou arquivo inválido.")
                    except Exception as e:
                        st.error(f"Erro: {e}")
                else:
                    st.warning("Preencha o nome e selecione um arquivo.")

        with tab_edit:
            st.subheader("Corrigir simulado existente")
            exames = self.repo.get_all_exam_names()
            exame_alvo = st.selectbox("Escolha o exame para editar:", [""] + exames, key="edit_select")
            
            if exame_alvo:
                # Carregamos as questões para edição[cite: 18, 19]
                questoes_originais = self.repo.load_exam(exame_alvo)
                
                # Reconstruímos o texto no padrão do parser (Q1... Answer:...)
                texto_reconstruido = ""
                for i, q in enumerate(questoes_originais):
                    texto_reconstruido += f"\nQ{i+1}\t{q.enunciado}\n"
                    for alt in q.alternativas:
                        texto_reconstruido += f"{alt}\n"
                    texto_reconstruido += f"Answer: {q.correta}\n"
                    if q.explicacao:
                        texto_reconstruido += f"Explanation: {q.explicacao}\n"
                
                # Área de edição manual
                novo_texto = st.text_area("Edite o conteúdo abaixo:", value=texto_reconstruido, height=400)
                
                if st.button("💾 Salvar Alterações", type="primary"):
                    exam_editado = ExamParser.parse_raw_text(exame_alvo, novo_texto)
                    if self.repo.update_exam(exam_editado):
                        st.success("✅ Simulado atualizado com sucesso!")
                        st.rerun()
                        
    def render_exam(self):
        idx = st.session_state.idx
        q = st.session_state.questoes[idx]
        total = len(st.session_state.questoes)

        st.subheader(f"Questão {idx + 1} de {total}")
        st.progress((idx + 1) / total)
        
        if not st.session_state.finalizado:
            st.markdown(f"### {q.enunciado}")
            
            # Regex aprimorada para capturar variações como (Choose two), (Choose two.), (choose 2) etc.
            is_multiple = bool(re.search(r'choose\s+(two|three|four|five|\d)', q.enunciado, re.IGNORECASE))

            if is_multiple:
                st.info("💡 Selecione múltiplas respostas para esta questão.")
                respostas_atuais = st.session_state.respostas.get(idx, "")
                selecionadas = []
                
                for i, opt in enumerate(q.alternativas):
                    # Mapeia o índice para letra: 0->A, 1->B...
                    letra = chr(65 + i) 
                    marcado = letra in respostas_atuais
                    if st.checkbox(opt, value=marcado, key=f"check_{idx}_{i}"):
                        selecionadas.append(letra)
                
                st.session_state.respostas[idx] = "".join(sorted(selecionadas))
            else:
                # Lógica para escolha única (Radio)
                resp_anterior = st.session_state.respostas.get(idx)
                idx_radio = None
                if resp_anterior:
                    # Converte letra de volta para índice para o rádio
                    idx_radio = ord(resp_anterior) - 65 if len(resp_anterior) == 1 else None
                
                escolha = st.radio("Selecione a alternativa:", q.alternativas, index=idx_radio, key=f"radio_{idx}")
                if escolha:
                    # Salva apenas a letra correspondente ao índice da opção
                    st.session_state.respostas[idx] = chr(65 + q.alternativas.index(escolha))

            st.divider()

            # Botões de Navegação (Sempre visíveis no final do container)
            c1, c2, c3 = st.columns([2, 6, 2])
            with c1:
                if st.button("⬅️ Anterior", use_container_width=True) and idx > 0:
                    st.session_state.idx -= 1
                    st.rerun()
            with c3:
                if idx < total - 1:
                    if st.button("Próximo ➡️", use_container_width=True):
                        st.session_state.idx += 1
                        st.rerun()
                else:
                    if st.button("Finalizar 🏁", type="primary", use_container_width=True):
                        st.session_state.finalizado = True
                        st.rerun()
        else:
            self.render_results()

    def render_results(self):
        st.header("📊 Resumo do Exame")
        
        # Cálculo de acertos
        resultados = []
        acertos = 0
        for i, q in enumerate(st.session_state.questoes):
            user_resp = st.session_state.respostas.get(i, "N/A")
            correta = q.correta
            is_correto = user_resp == correta
            if is_correto:
                acertos += 1
            resultados.append({
                "indice": i + 1,
                "pergunta": q.enunciado,
                "sua_resp": user_resp,
                "correta": correta,
                "status": "✅" if is_correto else "❌",
                "explicacao": q.explicacao
            })

        total = len(st.session_state.questoes)
        score = (acertos / total) * 100
        
        # Exibição de métricas principais
        c1, c2 = st.columns(2)
        c1.metric("Pontuação Final", f"{score:.2f}%")
        c2.metric("Acertos", f"{acertos} de {total}")

        if score >= 70:
            st.success("STATUS: APROVADO (PASS) 🏆")
        else:
            st.error("STATUS: REPROVADO (FAIL) 🔴")

        st.divider()
        st.subheader("🔍 Revisão das Questões")

        # Filtro para ver todas ou apenas as que errou
        filtro = st.radio("Mostrar:", ["Todas", "Apenas Erros"], horizontal=True)

        for res in resultados:
            if filtro == "Apenas Erros" and res["status"] == "✅":
                continue
            
            with st.expander(f"{res['status']} Questão {res['indice']} - {res['pergunta'][:80]}..."):
                st.write(f"**Enunciado:** {res['pergunta']}")
                st.write(f"**Sua resposta:** :blue[{res['sua_resp']}]")
                st.write(f"**Resposta correta:** :green[{res['correta']}]")
                
                if res['explicacao']:
                    st.info(f"**Explicação Técnica:**\n\n{res['explicacao']}")
                else:
                    st.warning("Nenhuma explicação disponível para esta questão.")

        st.divider()
        st.subheader("📄 Exportar Resultados")
        
        # Nova opção de filtro para o PDF
        tipo_relatorio = st.radio(
            "Selecione o conteúdo do PDF:",
            ["Completo", "Apenas Erros"],
            horizontal=True,
            key="pdf_filter"
        )
        
        try:
            apenas_erros = (tipo_relatorio == "Apenas Erros")
            report = ExamReport()
            
            # Gera o PDF passando o novo filtro[cite: 23]
            pdf_bytes = bytes(report.generate(score, acertos, total, resultados, apenas_erros=apenas_erros))
            
            suffix = "Erros" if apenas_erros else "Completo"
            st.download_button(
                label=f"📥 Baixar Relatório ({suffix})",
                data=pdf_bytes,
                file_name=f"Resultado_{suffix}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")
        
        if st.button("Reiniciar Novo Simulado", type="primary"):
            # Limpa o estado da sessão mas mantém o banco de dados
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    ExamApp().run()
