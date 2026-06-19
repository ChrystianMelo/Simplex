# Simplex

Implementação do método Simplex de duas fases para o trabalho prático de
Pesquisa Operacional (DCC035).

O programa resolve problemas gerais de programação linear, convertendo-os para
a forma padrão e classificando o resultado como ótimo, ótimo com múltiplas
soluções, inviável ou ilimitado. São aceitos problemas de maximização e
minimização, restrições `<=`, `>=` e `==`, além de variáveis não negativas, não
positivas ou livres.

Quando aplicável, a saída apresenta a solução primal, o valor da função
objetivo e a solução dual. Para problemas inviáveis ou ilimitados, são
produzidos certificados correspondentes.

## Entrada

O arquivo de entrada segue o formato:

```text
número de variáveis
número de restrições
sinais das variáveis (1: não negativa, -1: não positiva, 0: livre)
max|min coeficientes da função objetivo
coeficientes relação lado direito
```

Exemplo:

```text
2
2
1 0
max 1 1
1 -1 <= 2
1 1 >= 1
```

## Execução

Requer Python 3.11 ou superior.

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
python src/main.py entrada.txt
```

Opções disponíveis:

```text
--decimals N
--digits N
--policy largest|bland|smallest
```

Exemplo:

```bash
python src/main.py entrada.txt --decimals 3 --digits 7 --policy bland
```

## Testes

```bash
pip install -r requirements.txt
pytest
```
