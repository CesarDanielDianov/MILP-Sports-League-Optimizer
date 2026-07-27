#!/usr/bin/env python3
import pulp
import sys

# ------------------------------
# Ler ficheiro da entrada padrão
# ------------------------------
linhas = [ln.strip() for ln in sys.stdin.readlines() if ln.strip()]

# Número de equipas e jogos já realizados
n, m = map(int, linhas[0].split())

# Lista de jogos realizados (usar índices 0..n-1)
jogos_realizados = []
for linha in linhas[1:]:
    i, j, r = map(int, linha.split())
    i -= 1
    j -= 1
    if r == 0:
        r_idx = -1   # empate
    else:
        r_idx = r - 1  # converter para 0-based
    jogos_realizados.append((i, j, r_idx))

# ------------------------------
# Função principal (igual que antes)
# ------------------------------
def calcular_min_wins(n, jogos_realizados):
    pontos = [0]*n
    jogos_feitos = set()
    for i, j, r in jogos_realizados:
        jogos_feitos.add((i,j))
        if r == -1:
            pontos[i] += 1
            pontos[j] += 1
        elif r == i:
            pontos[i] += 3
        elif r == j:
            pontos[j] += 3

    # Jogos restantes
    jogos_restantes = []
    for i in range(n):
        for j in range(n):
            if i != j and (i,j) not in jogos_feitos:
                jogos_restantes.append((i,j))

    resultados_min_wins = []

    if not jogos_restantes:
        max_p = max(pontos)
        for T in range(n):
            if pontos[T] >= max_p:
                resultados_min_wins.append(0)
            else:
                resultados_min_wins.append(-1)
        return resultados_min_wins

    for T in range(n):
        prob = pulp.LpProblem(f"Equipa_{T+1}", pulp.LpMinimize)
        W_vars = {}
        D_vars = {}
        L_vars = {}
        for (i, j) in jogos_restantes:
            W_vars[(i, j)] = pulp.LpVariable(f"W_{i}_{j}", cat="Binary")
            D_vars[(i, j)] = pulp.LpVariable(f"D_{i}_{j}", cat="Binary")
            L_vars[(i, j)] = pulp.LpVariable(f"L_{i}_{j}", cat="Binary")
            prob += W_vars[(i, j)] + D_vars[(i, j)] + L_vars[(i, j)] == 1

        pontos_finais = []
        for k in range(n):
            expr = pulp.LpAffineExpression()
            expr += pontos[k]
            for (i, j) in jogos_restantes:
                if k == i:
                    expr += 3 * W_vars[(i, j)]
                    expr += 1 * D_vars[(i, j)]
                elif k == j:
                    expr += 3 * L_vars[(i, j)]
                    expr += 1 * D_vars[(i, j)]
            pontos_finais.append(expr)

        for j in range(n):
            if j != T:
                prob += pontos_finais[T] >= pontos_finais[j]

        termos_vitorias_T = []
        for (i, j) in jogos_restantes:
            if i == T:
                termos_vitorias_T.append(W_vars[(i, j)])
            if j == T:
                termos_vitorias_T.append(L_vars[(i, j)])
        soma_vitorias = pulp.lpSum(termos_vitorias_T)
        prob += soma_vitorias

        status = prob.solve(pulp.PULP_CBC_CMD(msg=0))
        if pulp.LpStatus[prob.status] == "Optimal":
            val = pulp.value(soma_vitorias)
            if val is not None:
                resultados_min_wins.append(int(round(val)))
            else:
                resultados_min_wins.append(-1)
        else:
            resultados_min_wins.append(-1)


# ------------------------------
# Executar e imprimir resultados
# ------------------------------
resultados = calcular_min_wins(n, jogos_realizados)
for r in resultados:
    print(r)
