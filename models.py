from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Question:
    enunciado: str
    alternativas: List[str]
    correta: str
    explicacao: Optional[str] = ""

@dataclass
class Exam:
    nome: str
    questoes: List[Question] = field(default_factory=list)
