# 🐾 PetCare

Sistema web de gestão para clínica veterinária, com cadastro de tutores, pets e agendamentos, autenticação de usuários e proteção de dados pessoais.

---

## 📋 Sobre o projeto

O **PetCare** foi desenvolvido para resolver problemas comuns em clínicas veterinárias que ainda utilizam controle manual de informações, como perda de consultas, duplicidade de dados e falhas no armazenamento. O sistema centraliza o gerenciamento de tutores, pets e agendamentos em uma interface intuitiva e segura.

### Funcionalidades principais

- **Autenticação de usuários** com sessão de 30 minutos e senhas criptografadas (PBKDF2 + salt).
- **Cadastro e gerenciamento de tutores** (dados pessoais, contato e endereço completo).
- **Cadastro e gerenciamento de pets**, com vínculo obrigatório a um tutor.
- **Agendamentos** com validação de duplicidade e controle de status (Agendado, Concluído, Cancelado).
- **Busca em tempo real** em tutores e pets.
- **Filtros** de data e status nos agendamentos.
- **Dashboard** com navegação entre os módulos.

---

## 🛠️ Tecnologias utilizadas

### Backend
- **Python 3.12**
- **Flask** (framework web)
- **SQLite3** (banco de dados)
- **Werkzeug** (hash de senhas)
- **PBKDF2 + salt** (criptografia de senhas)

### Frontend
- **HTML5**
- **CSS3** (responsivo, sem frameworks)
- **JavaScript puro** (fetch API, manipulação de DOM)

---

## 📁 Estrutura do projeto
petcare/
├── app.py # Ponto de entrada do Flask
├── requirements.txt # Dependências do projeto
├── .gitignore
│
├── db/
│ └── db.py # Script de criação e população do banco
│
├── models/ # Camada de dados
│ ├── init.py
│ ├── user_model.py
│ ├── tutor_model.py
│ ├── pet_model.py
│ └── agendamento_model.py
│
├── routes/ # Camada de rotas (Blueprints)
│ ├── init.py
│ ├── auth_routes.py
│ ├── dashboard_routes.py
│ ├── tutor_routes.py
│ ├── pet_routes.py
│ └── agendamento_routes.py
│
├── templates/ # HTMLs (Jinja2)
│ ├── index.html # Login + Cadastro
│ └── pages/
│ ├── dashboard.html
│ ├── t.html # Tutores
│ ├── p.html # Pets
│ └── a.html # Agendamentos
│
└── static/
├── css/
│ ├── index.css
│ ├── dashboard.css
│ ├── managing.css
│ └── agendamento.css
├── js/
│ ├── alternar_aba.js
│ ├── usuario_conectado.js
│ ├── auto_dismiss.js
│ ├── tutor.js
│ ├── pet.js
│ └── agendamento.js
└── assets/
├── tutor_com_pet.svg
├── pet_interrogacao.svg
└── agenda_check.svg


---
## 🗄️ Modelagem do banco de dados

O sistema utiliza 4 tabelas com relacionamentos:

| Tabela | Descrição |
| :--- | :--- |
| `usuarios` | Usuários do sistema (login por CPF, senha com hash) |
| `tutores` | Clientes da clínica (dados pessoais e endereço) |
| `pets` | Animais, com vínculo obrigatório a um tutor (`tutor_id`) |
| `agendamentos` | Consultas/serviços, com vínculo a um pet (`pet_id`) |

**Relacionamentos:**
- `pets.tutor_id` → `tutores.id` (FOREIGN KEY)
- `agendamentos.pet_id` → `pets.id` (FOREIGN KEY)

---

## 🔒 Segurança e LGPD

- Senhas armazenadas como **hash PBKDF2 com salt aleatório** por usuário.
- Comparação de senha com `secrets.compare_digest` (evita timing attacks).
- Sessão com expiração de **30 minutos** (configurável em `app.py`).
- Rotas protegidas por verificação de sessão (`_login_obrigatorio`).
- APIs retornam `401` se o usuário não estiver autenticado.

---

## 🚀 Como executar o projeto

### Pré-requisitos
- Python 3.10+
- pip

### Passo a passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/petcare.git
   cd petcare

2. **Crie e ative um ambiente virtual (recomendado)**
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate

3. **Instale as Dependencias**
     pip install -r requirements.txt

4. **Crie e popule o banco de dados**
     python db/db.py
     Isso criará o arquivo petcare.db na raiz do projeto com as tabelas e os dados iniciais.

5. **Execute a Aplicação**
     python app.py

6. **Acesse no navegador**
     http://127.0.0.1:5000

📄 Licença

Este projeto é de uso educacional. Sinta-se livre para estudar, modificar e reutilizar o código.

👤 Autor

Desenvolvido por Silvartt.

---

## ✅ Como usar

1. Crie o arquivo `README.md` na **raiz do projeto** (mesma pasta do `app.py`).
2. Cole o conteúdo acima.
3. No terminal, na raiz do projeto:
   ```bash
   git add README.md
   git commit -m "Adiciona README com documentação do projeto"
   git push
