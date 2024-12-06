import json
import websocket
from collections import defaultdict, deque
import time
import requests
import heapq

GRUPO_ID = "f68e8e5c-5646-44b7-b2c7-bce258e7c114"
LABIRINTO_ID = 1
WEBSOCKET_URL = f"ws://localhost:8000/ws/{GRUPO_ID}/{LABIRINTO_ID}"

def interpretar_resposta_bruta(resposta):
    try:
        partes = resposta.split(", Adjacentes")
        if len(partes) < 2:
            raise ValueError("Formato inesperado da resposta. Não encontrado o campo 'Adjacentes'.")
        
        vertice_info = partes[0].split(", ")
        vertice_atual = int(vertice_info[0].split(":")[1].strip())
        tipo = int(vertice_info[1].split(":")[1].strip())
        
        adjacentes_str = partes[1].split(":")[1].strip()
        adjacentes = [vertice for vertice, peso in eval(adjacentes_str)]
        
        return vertice_atual, tipo, adjacentes
    except Exception as e:
        print(f"Erro ao interpretar a resposta bruta: {e}")
        return None, None, []

def busca_bidir(grafo, start, goal):
    # Fila para as buscas de início e fim
    queue_start = deque([start])
    queue_goal = deque([goal])
    
    # Dicionários de pais para reconstruir o caminho
    parent_start = {start: None}
    parent_goal = {goal: None}
    
    # Conjuntos de visitados para evitar revisitas
    visited_start = {start}
    visited_goal = {goal}
    
    while queue_start and queue_goal:
        # Expande a partir do início
        current_start = queue_start.popleft()
        for neighbor in grafo[current_start]:
            if neighbor not in visited_start:
                visited_start.add(neighbor)
                parent_start[neighbor] = current_start
                queue_start.append(neighbor)
                if neighbor in visited_goal:
                    return reconstruct_path(parent_start, parent_goal, neighbor)

        # Expande a partir do fim
        current_goal = queue_goal.popleft()
        for neighbor in grafo[current_goal]:
            if neighbor not in visited_goal:
                visited_goal.add(neighbor)
                parent_goal[neighbor] = current_goal
                queue_goal.append(neighbor)
                if neighbor in visited_start:
                    return reconstruct_path(parent_start, parent_goal, neighbor)

    return None

def reconstruct_path(parent_start, parent_goal, meeting_point):
    # Reconstrói o caminho completo
    path = []
    
    # Caminho do início até o ponto de encontro
    current = meeting_point
    while current is not None:
        path.append(current)
        current = parent_start.get(current)
    path.reverse()

    # Caminho do fim até o ponto de encontro
    current = parent_goal.get(meeting_point)
    while current is not None:
        path.append(current)
        current = parent_goal.get(current)

    return path

def heuristic(vertice, goal, tipo='manhattan'):
    return abs(vertice - goal)  # Simplificação para acelerar

def explorar_labirinto():
    try:
        ws = websocket.create_connection(WEBSOCKET_URL)
        print(f"Conexão WebSocket estabelecida: {WEBSOCKET_URL}")

        comando = {"action": "enter_labyrinth", "parameters": {"labyrinth_id": LABIRINTO_ID}}
        ws.send(json.dumps(comando))
        print("Entrando no labirinto...")

        grafo = defaultdict(list)
        pesos = {}
        tipos = {}
        visitados = set()
        tempo_inicio = time.time()
        vertice_entrada = None
        vertice_saida = None
        vertices_explorados = 0
        caminho = []

        while True:
            resposta_bruta = ws.recv()
            print(f"Resposta recebida: {resposta_bruta}")

            if "Comando não reconhecido" in resposta_bruta:
                print("Comando não reconhecido. Tentando ajustar.")
                continue

            vertice_atual, tipo, adjacentes = interpretar_resposta_bruta(resposta_bruta)
            if vertice_atual is None:
                raise ValueError("Não foi possível interpretar a resposta do labirinto.")

            tipos[vertice_atual] = tipo
            grafo[vertice_atual].extend(adjacentes)
            visitados.add(vertice_atual)
            vertices_explorados += 1
            caminho.append(vertice_atual)

            if tipo == 1 and vertice_entrada is None:
                vertice_entrada = vertice_atual
            if tipo == 2 and vertice_saida is None:
                vertice_saida = vertice_atual
                print(f"Saída encontrada no vértice: {vertice_atual}")
                break

            proximo = None
            for vizinho in adjacentes:
                if vizinho not in visitados:
                    proximo = vizinho
                    break
            print(type(adjacentes))
            if proximo is None:
                print("Não há mais vértices para visitar. Caminho encerrado.")
                break

            comando_mover = f"ir: {proximo}"
            ws.send(comando_mover)
            print(f"Movendo para o vértice: {proximo}")

        tempo_fim = time.time()
        print("Exploração encerrada.")
        print(f"Tempo total de exploração: {tempo_fim - tempo_inicio:.2f} segundos")

        verificar_conexoes(caminho, grafo)
        finalizar_labirinto(vertice_entrada, vertice_saida, caminho)

        ws.close()

        obter_placar()

    except websocket.WebSocketException as e:
        print(f"Erro na conexão WebSocket: {e}")
    except Exception as e:
        print(f"Erro geral: {e}")

def verificar_conexoes(caminho, grafo):
    for i in range(len(caminho) - 1):
        vertice_atual = caminho[i]
        vertice_proximo = caminho[i + 1]
        if vertice_proximo not in grafo[vertice_atual]:
            print(f"Atenção: Vértices {vertice_atual} e {vertice_proximo} não estão conectados corretamente!")
            raise ValueError(f"Caminho inválido: vértices {vertice_atual} e {vertice_proximo} não estão conectados")

def finalizar_labirinto(vertice_entrada, vertice_saida, caminho):
    try:
        dados = {
            "labirinto": LABIRINTO_ID,
            "grupo": GRUPO_ID,
            "vertices": caminho
        }

        url_resposta = "http://localhost:8000/resposta"
        resposta = requests.post(url_resposta, json=dados)

        if resposta.status_code == 200:
            print("Labirinto concluído com sucesso!")
        else:
            print(f"Erro ao enviar para API: {resposta.status_code}, {resposta.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar dados para a API: {e}")

def obter_placar():
    try:
        url_placar = "http://localhost:8000/placar"
        resposta = requests.get(url_placar)

        if resposta.status_code == 200:
            placar = resposta.json()
            print("\nPlacar Geral:")
            for grupo in placar:
                print(f"\nGrupo: {grupo['grupo']}")
                for labirinto in grupo['labirintos']:
                    print(f"  Labirinto: {labirinto['labirinto']}, Passos: {labirinto['passos']}, Exploração: {labirinto['exploracao']} segundos")
        else:
            print(f"Erro ao obter o placar: {resposta.status_code}, {resposta.json()}")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao solicitar o placar: {e}")

if __name__ == "__main__":
    explorar_labirinto()