# parser_engine.py
import re
import fitz  # PyMuPDF
from models import Question, Exam

class ExamParser:
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """Extrai todo o texto de um arquivo PDF."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text

    @staticmethod
    def parse_raw_text(nome_exame: str, text: str) -> Exam:
        exam = Exam(nome=nome_exame)
        blocks = re.split(r'\nQ\d+\t|\nQuestion #:\d+', text)
        
        for block in blocks:
            if not block.strip(): continue
            lines = block.strip().split('\n')
            enunciado_parts, alts, correct, expl = [], [], "", ""
            state = "enunciado"
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                if re.match(r'^([A-E]|[1-5])\.', line):
                    state = "alternativas"
                    alts.append(line)
                elif line.startswith("Answer:"):
                    state = "resposta"
                    # CAPTURA A RESPOSTA (ex: 'B' ou 'AB')[cite: 11, 14]
                    correct = line.replace("Answer:", "").replace(" ", "").strip() 
                elif line.startswith(("Explanation", "Key takeaway")):
                    state = "explicacao"
                    expl = line
                elif state == "enunciado":
                    enunciado_parts.append(re.sub(r'^-?\s*\[.*?\]', '', line).strip())
                elif state == "explicacao":
                    expl += " " + line
            
            if enunciado_parts and alts:
                # ADICIONADO 'correct' AQUI PARA SALVAR A RESPOSTA CERTA[cite: 14, 15]
                exam.questoes.append(Question(" ".join(enunciado_parts), alts, correct, expl))
        return exam
        
    @staticmethod
    def _identificar_multipla_escolha(enunciado: str) -> bool:
        # Procura por padrões como (Choose two), (Choose three), etc
        return bool(re.search(r'\(Choose \w+\)', enunciado, re.IGNORECASE))
