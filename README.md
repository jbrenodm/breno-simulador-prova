# 🛡️ Breno Exam Simulator

Um simulador de exames robusto desenvolvido em Python para auxiliar profissionais de TI e Cybersecurity na preparação para certificações. O sistema permite importar simulados de arquivos TXT ou PDF, realizar testes práticos e gerar relatórios de desempenho personalizados.

## 🚀 Funcionalidades

- **Importação Inteligente**: Motor de parsing para extrair questões de PDFs e arquivos de texto.
- **Simulação Realista**: Lógica para questões de múltipla escolha e escolha única, incluindo suporte a "(Choose two/three)".
- **Banco de Dados Local**: Persistência de dados utilizando SQLite para gerenciar múltiplos simulados.
- **Gerenciador de Ciclo de Vida**: Interface para carregar, editar, corrigir e excluir simulados existentes.
- **Relatórios em PDF**: Geração de relatórios de desempenho completos ou focados apenas nos erros, com tratamento de caracteres especiais.

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: [Python 3.12+](https://www.python.org/)
- **Interface**: [Streamlit](https://streamlit.io/)
- **Banco de Dados**: [SQLite](https://www.sqlite.org/)
- **Manipulação de PDF**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- **Geração de Relatórios**: [FPDF2](https://py-pdf.github.io/fpdf2/)

## 📋 Pré-requisitos

Antes de começar, você precisará ter o Python instalado. Como este projeto foi desenvolvido no **Zorin OS**, as instruções abaixo seguem o padrão Linux (Debian/Ubuntu).

```bash
### Instalar dependências do sistema para o PyMuPDF
sudo apt update
sudo apt install python3-pip python3-venv
🔧 Instalação e Execução
```

###Clone o repositório:
```Bash
git clone [https://github.com/SEU_USUARIO/breno-exam-simulator.git](https://github.com/SEU_USUARIO/breno-exam-simulator.git)
cd breno-exam-simulator
```

###Crie e ative o ambiente virtual:
```Bash
python3 -m venv venv
source venv/bin/activate
```

###Instale as dependências:
```Bash
pip install -r requirements.txt
```

###Execute a aplicação:
```Bash
streamlit run app.py
```