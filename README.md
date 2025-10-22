# Site do NEMO

Bem-vindo ao repositório oficial do site do NEMO (Núcleo de Estudos de Matemática Olímpica), um grupo de extensão da USP de São Carlos dedicado à matemática competitiva e à resolução de problemas.

## Sobre Este Projeto

Este projeto é uma aplicação web baseada em Flask que serve como uma das presenças online do NEMO. Ele possui um blog para notícias e artigos, uma seção para os Problemas do Mês e páginas com informações sobre o grupo, seus membros e materiais de estudo.

## Funcionalidades

-   **Gerenciamento de Conteúdo com Arquivos:** Posts e artigos são escritos em Markdown e gerenciados através da extensão Flask-FlatPages, tornando a criação de conteúdo simples e acessível.
-   **Autenticação de Usuários:** O site possui um sistema completo de autenticação de usuários, permitindo que membros façam login e gerenciem o conteúdo.
-   **Editor de Posts:** Um editor de Markdown no navegador está disponível para criar e editar publicações.
-   **Implantação com Docker:** A aplicação é totalmente containerizada com Docker e pronta para implantação em produção com o Gunicorn.
-   **Segurança Integrada:** A aplicação inclui proteção contra CSRF em todos os formulários e sanitiza o conteúdo gerado por usuários para prevenir ataques de XSS.

## Como Começar

Você pode executar este projeto localmente para desenvolvimento ou testes. Existem duas maneiras recomendadas para configurar a aplicação: usando Docker (recomendado para um ambiente limpo e isolado) ou configurando-a diretamente em sua máquina.

### Pré-requisitos

-   Python 3.10+
-   Docker (se for usar a configuração com Docker)

### Opção 1: Executando com Docker (Recomendado)

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd <diretorio-do-repositorio>
    ```

2.  **Crie um arquivo de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto e adicione o seguinte conteúdo. **Certifique-se de alterar a `SECRET_KEY` para uma string nova e aleatória.**
    (Se não funcionar inicialmente, tente remover a linha do `DATABASE_URL` tente prosseguir)
    ```
    SECRET_KEY='sua_chave_super_secreta_aqui'
    DATABASE_URL='sqlite:///posts.db'
    ```

3.  **Construa a imagem Docker:**
    ```bash
    sudo docker build -t nemo-app .
    ```

4.  **Execute o contêiner Docker:**
    Para garantir que seus posts, uploads e o banco de dados sejam salvos permanentemente, execute o contêiner com volumes, que conectam pastas do seu computador ao contêiner:
    ```bash
    sudo docker run -p 8000:8000 \
      -v $(pwd)/posts:/app/posts \
      -v $(pwd)/instance:/app/instance \
      -v $(pwd)/static/uploads:/app/static/uploads \
      --env-file .env \
      nemo-app
    ```

5.  A aplicação estará disponível em [http://localhost:8000](http://localhost:8000).

### Opção 2: Configuração Local

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd <diretorio-do-repositorio>
    ```

2.  **Crie um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Crie um arquivo de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto e adicione o seguinte conteúdo. **Certifique-se de alterar a `SECRET_KEY` para uma string nova e aleatória.**
    ```
    SECRET_KEY='sua_chave_super_secreta_aqui'
    DATABASE_URL='sqlite:///posts.db'
    ```

5.  **Execute a aplicação:**
    ```bash
    venv/bin/python app.py
    ```

6.  A aplicação estará disponível em [http://localhost:5000](http://localhost:5000).

## Criando um Usuário

Para criar um novo usuário com permissões de gerenciamento de conteúdo, você pode usar o script `create_user.py`. Execute o seguinte comando e siga as instruções:

```bash
venv/bin/python create_user.py
```

## Estrutura do Projeto

-   `app.py`: O ponto de entrada principal para a aplicação Flask.
-   `config.py`: Contém as configurações da aplicação.
-   `models.py`: Define os modelos do banco de dados (ex., o modelo `User`).
-   `routes.py`: Contém todas as funções de visualização e rotas da aplicação.
-   `templates/`: Armazena todos os templates Jinja2 para o frontend da aplicação.
-   `static/`: Contém todos os arquivos estáticos (CSS, JavaScript, imagens).
-   `posts/`: O diretório raiz para todo o conteúdo baseado em Markdown.
-   `Dockerfile`: A receita para construir a imagem Docker da aplicação.
-   `gunicorn_config.py`: Configuração para o servidor web Gunicorn.

---
