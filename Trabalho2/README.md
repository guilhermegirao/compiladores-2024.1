# Trabalho 2 - Compiladores 2024.1
## Seleção de instrução:

### Como instalar?
Caso seu ambiente não seja unix, recomendamos o uso de **Docker**, pois para a questão 1, utilizamos a biblioteca `graphviz` para gerar a imagem da árvore, a qual necessita de ser instalada.

#### Via Docker:
Instale o **Docker** para poder rodar o projeto "conteinerizado" e com as dependências já instaladas e configuradas com:
```shell
docker compose up -d --build
docker exec -it compiladores-2 /bin/bash # Lembrando, que você pode trocar o nome do container
```

#### Instalação na máquina:
Caso não queira utilizar Docker, instale o `Python3` na sua máquina e instale a biblioteca `graphviz` com:
```shell
sudo apt-get install graphviz -y
pip install -r requirements.txt
```

### Como rodar?
Quando o terminal abrir, você poderá rodar o projeto normalmente com:
```shell
python3 main.py
```

> Para definir uma ***entrada***, é só criar *n* arquivos `.txt` em **__tests\__/** contendo um conjunto de instruções no formato linear.

> Aas ***saídas*** da questão 1 estarão em: **__outputs\__/tree_graph**

### Equipe:
- Eliton Lima
- Guilherme Girão
- Igor Gabriel
- Roberto de Oliveira
