# Simplex de duas fases

Implementação do método Simplex para o trabalho prático de DCC035 — Pesquisa
Operacional (2026.1).

O programa:

- converte PLs gerais para a Forma Padrão de Igualdades (FPI);
- trata variáveis não negativas, não positivas e livres;
- executa a Fase I para encontrar uma base viável;
- identifica problemas inviáveis, ilimitados e com múltiplas soluções ótimas;
- imprime a FPI, os tableaus, as bases e cada operação de pivoteamento;
- oferece as políticas `largest`, `bland` e `smallest`;
- imprime solução primal e dual quando existe solução ótima.

## Instalação

Requer Python 3.11 ou mais recente.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

Também é possível usar:

```bash
./scripts/config.sh
```

## Execução

```bash
python3 src/main.py arquivo.lp \
  --decimals 3 \
  --digits 7 \
  --policy bland
```

Ou, após configurar o ambiente:

```bash
./scripts/run.sh arquivo.lp --decimals 3 --digits 7 --policy bland
```

As opções são:

- `--decimals`: número de casas decimais;
- `--digits`: largura mínima usada para imprimir cada número;
- `--policy`: `largest` (padrão), `bland` ou `smallest`.

## Formato de entrada

O parser aceita o formato literal do enunciado:

```text
2
2
1 0
1 1
1 -1 <= 2
1 1 >= 1
```

Nesse formato, a função objetivo é considerada de maximização. Também é aceito
o formato explícito usado nos casos de teste:

```text
2
2
1 0
max 1 1
1 -1 <= 2
1 1 >= 1
```

Use `min` no lugar de `max` para problemas de minimização.

## Saída

Antes do resultado final, são impressos:

1. a PL transformada em FPI;
2. o tableau inicial e as iterações da Fase I;
3. o tableau inicial e as iterações da Fase II;
4. as variáveis que entram e saem da base.

As variáveis são indexadas a partir de zero (`x0`, `x1`, ...), como solicitado
no enunciado.

## Testes

```bash
venv/bin/pytest -q
```

Ou:

```bash
./scripts/run_tests.sh
```

A suíte cobre os casos fornecidos, a interface de linha de comando, as três
políticas de pivoteamento, degenerescência, ciclagem e múltiplos ótimos.
