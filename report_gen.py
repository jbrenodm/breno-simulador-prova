from fpdf import FPDF
from datetime import datetime

class ExamReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "Breno Exam Simulator - Relatório de Desempenho", 0, 1, "C")
        self.ln(5)

    def clean_text(self, text):
        """Substitui caracteres Unicode problematicos por equivalentes ASCII."""
        if not text:
            return ""
        replacements = {
            "—": "-",  # em dash
            "–": "-",  # en dash
            "“": '"',  # smart quotes
            "”": '"',
            "‘": "'",
            "’": "'",
            "…": "...",
            "\u200b": "", # zero width space (comum em PDFs)
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Remove caracteres que nao podem ser codificados em 'latin-1'
        return text.encode('latin-1', 'ignore').decode('latin-1')
    
    def generate(self, score, acertos, total, resultados, apenas_erros=False):
        self.add_page()
        effective_page_width = self.w - 2 * self.l_margin
        
        # Título dinâmico baseado no filtro
        titulo = "Relatorio de Erros" if apenas_erros else "Relatorio de Desempenho Completo"
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, self.clean_text(f"Breno Exam Simulator - {titulo}"), 0, 1, "C")
        self.ln(5)

        # Resumo (Mantenha o resumo geral para contexto técnico)
        self.set_font("helvetica", "B", 11)
        self.set_fill_color(240, 240, 240)
        self.cell(effective_page_width, 10, self.clean_text(f"Pontuacao: {score:.2f}% ({acertos} de {total} acertos)"), 1, 1, 'L', True)
        self.ln(10)

        for res in resultados:
            # Lógica de Filtro: Pula acertos se o usuário pediu apenas erros
            if apenas_erros and res['status'] == "✅":
                continue
                
            self.set_x(self.l_margin)
            self.set_font("helvetica", "B", 10)
            status_txt = "CORRETA" if res['status'] == "✅" else "ERRADA"
            self.multi_cell(effective_page_width, 8, self.clean_text(f"Questao {res['indice']} - [{status_txt}]"), align='L')
            
            self.set_font("helvetica", "", 10)
            self.set_x(self.l_margin)
            self.multi_cell(effective_page_width, 6, self.clean_text(f"Pergunta: {res['pergunta']}"), align='L')
            
            self.ln(1)
            self.set_x(self.l_margin)
            self.multi_cell(effective_page_width, 6, self.clean_text(f"Sua Resposta: {res['sua_resp']} | Correta: {res['correta']}"), align='L')
            
            if res['explicacao']:
                self.ln(1)
                self.set_x(self.l_margin)
                self.set_text_color(80, 80, 80)
                self.multi_cell(effective_page_width, 5, self.clean_text(f"Explicacao: {res['explicacao']}"), align='L')
                self.set_text_color(0, 0, 0)
            
            self.ln(5)
            self.line(self.l_margin, self.get_y(), self.w - self.l_margin, self.get_y())
            self.ln(5)
            
        return self.output()