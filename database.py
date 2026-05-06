import sqlite3
import json
from typing import List
from models import Question, Exam

class ExamRepository:
    def __init__(self, db_path='simulados.db'):
        self.db_path = db_path
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        with self._connect() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS exames 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS questoes 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, exame_id INTEGER, 
                             enunciado TEXT, alternativas TEXT, correta TEXT, explicacao TEXT,
                             FOREIGN KEY(exame_id) REFERENCES exames(id))''')

    def save_exam(self, exam: Exam) -> bool:
        try:
            with self._connect() as conn:
                cursor = conn.execute("INSERT INTO exames (nome) VALUES (?)", (exam.nome,))
                exame_id = cursor.lastrowid
                for q in exam.questoes:
                    conn.execute('''INSERT INTO questoes (exame_id, enunciado, alternativas, correta, explicacao) 
                                    VALUES (?, ?, ?, ?, ?)''', 
                                 (exame_id, q.enunciado, json.dumps(q.alternativas), q.correta, q.explicacao))
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_exam_names(self):
        with self._connect() as conn:
            return [row[0] for row in conn.execute("SELECT nome FROM exames").fetchall()]

    def load_exam(self, name: str) -> List[Question]:
        with self._connect() as conn:
            rows = conn.execute('''SELECT enunciado, alternativas, correta, explicacao FROM questoes 
                                   JOIN exames ON exames.id = questoes.exame_id WHERE exames.nome = ?''', (name,)).fetchall()
            return [Question(r[0], json.loads(r[1]), r[2], r[3]) for r in rows]
        
    def delete_exam(self, name: str) -> bool:
        """Remove um exame e todas as suas questões do banco de dados."""
        try:
            with self._connect() as conn:
                # O SQLite removerá as questões automaticamente se o ON DELETE CASCADE estiver ativo,
                # caso contrário, removemos manualmente primeiro.
                exame_id = conn.execute("SELECT id FROM exames WHERE nome = ?", (name,)).fetchone()
                if exame_id:
                    conn.execute("DELETE FROM questoes WHERE exame_id = ?", (exame_id[0],))
                    conn.execute("DELETE FROM exames WHERE id = ?", (exame_id[0],))
                    return True
            return False
        except Exception as e:
            print(f"Erro ao deletar: {e}")
            return False
        
    def update_exam(self, exam: Exam) -> bool:
        """Atualiza um exame existente removendo as questões antigas e inserindo as novas."""
        try:
            with self._connect() as conn:
                # Busca o ID do exame pelo nome
                row = conn.execute("SELECT id FROM exames WHERE nome = ?", (exam.nome,)).fetchone()
                if not row:
                    return False
                exame_id = row[0]
                
                # Remove questões antigas
                conn.execute("DELETE FROM questoes WHERE exame_id = ?", (exame_id,))
                
                # Insere as novas questões
                for q in exam.questoes:
                    conn.execute('''INSERT INTO questoes (exame_id, enunciado, alternativas, correta, explicacao) 
                                    VALUES (?, ?, ?, ?, ?)''', 
                                 (exame_id, q.enunciado, json.dumps(q.alternativas), q.correta, q.explicacao))
            return True
        except Exception as e:
            print(f"Erro ao atualizar: {e}")
            return False
