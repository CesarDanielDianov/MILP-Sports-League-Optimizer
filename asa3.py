import pulp
import sys

linhas=[]
for ln in sys.stdin.readlines():
    ln=ln.strip()                       #vai linha a linha (ln) das sys.stdin....etc ,tira os espaços e mete                        
    linhas.append(ln)                   # na lista 


cabeçalho=linhas[0].split()
eq=int(cabeçalho[0])             #transofrmar os valores de cabeçalho de Strings->Integrer pra usar depois
jg=int(cabeçalho[1])
print(linhas)

jogos_feitos=set()
for linha in linhas[1:]:    #passa a lista com strings para uma lista de tuplos com 3 elemntos
    partes=linha.split()
    i=int(partes[0])
    j=int(partes[1])
    rslt=int(partes[2])

    jogos_feitos.add((i,j,rslt))
    

print(jogos_feitos)

pontos=[0]*eq            #cria um vetor pra guardar os pontos de tamanho n so com 0's
for (i,j,rslt) in jogos_feitos:
    if rslt==i:
        pontos[i-1]+=3
    elif rslt==j:
        pontos[j-1]+=3
    elif rslt==0:
        pontos[i-1]+=1
        pontos[i-1]+=1
print(pontos)

def funçao_principal(n,jogos_feitos):
    #lista com os jogos que faltam
    #aplicaçao do pulp->Definir as variaveis do pulp (win draw defeat) e o objetivo (Minimize)
    # passar a expressao Pf=Pa+(3*W)+(D) como pulp.LpAffineExpression() (ou seja passas Pf a uma expressao que o solver pode manipular)
    # metes as restriçoes necessarias( Pf da nossa team temd e ser maior que o Pf sas outrs)
    #se a soluçao for encontrado o solver vai devolver o numero de wins Minimas com as restriçoes todas obedecidas
    #caso contrario se nao houver soluçao possivel devolve -1