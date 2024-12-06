import asyncio
import websockets
import json
from datetime import datetime
from config import WEBSOCKET_URL, LABIRINTO_ID, labirinto_id_hex
from utils.maze_validator import MazeValidator
from algorithms.bidirectional_search import bidirectional_search
from services.api_service import submit_maze_solution, get_scoreboard

class MazeExplorer:
    def __init__(self):
        self.graph = {}
        self.types = {}
        self.visited = []
        self.path = []
        self.entry_vertex = None
        self.exit_vertex = None

    async def explore(self):
        start_time = datetime.now()
        
        try:
            async with websockets.connect(WEBSOCKET_URL) as ws:
                print("WebSocket connection established")
                
                # Enter the labyrinth
                enter_command = {"action": "enter_labyrinth", "parameters": {"labyrinth_id": LABIRINTO_ID}}
                await ws.send(json.dumps(enter_command))
                
                await self.explore_maze(ws)

            exploration_time = (datetime.now() - start_time).total_seconds()
            print(f"\nExploration completed in {exploration_time:.2f} seconds")
            
            self.print_exit_and_path()
            await self.finalize_maze()
            #await self.display_scoreboard()
            
        except Exception as e:
            print(f"Exploration error: {e}")
            raise
    
    async def explore_maze(self, ws, current_vertex=None):
        # Quando já está passando o current_vertex, faz a exploração normalmente
        response = await ws.recv()
        print(f"Resposta recebida: {response}")


        # Interpreta a resposta recebida
        current_vertex, vertex_type, adjacent = interpretar_resposta_bruta(response)
        
        # Verifica se o current_vertex é válido
        if current_vertex is None:
            print("Erro: Não foi possível obter um vértice válido. Finalizando a exploração.")
            return  # Se não receber um vértice válido, retorna

        # Validação do vértice
        MazeValidator.validate_vertex(current_vertex, vertex_type, adjacent)

        # Atualizando os dados do labirinto
        self.update_maze_data(current_vertex, vertex_type, adjacent)

        # Imprimindo os vértices adjacentes
        print(f"Vértices adjacentes do vértice {current_vertex}: {adjacent}")

        # Caso o tipo seja de saída, finaliza a exploração
        if vertex_type == 2:
            print(f"Saída encontrada no vértice {current_vertex}!")
            return

        # Caso contrário, percorre os vértices adjacentes
        for adj in adjacent:
            # Verifica se o vértice adjacente já foi visitado
            if adj not in self.visited:
                print(f"Movendo para o vértice {adj}...")

                # Envia o comando para mover para o vértice adjacente
                move_command = f"ir: {adj}"
                await ws.send(move_command)

                await self.explore_maze(ws, adj)

                return  # Após explorar um caminho, retorna para não continuar a iteração

        # Se não houver vértices adjacentes não visitados, faz backtracking
        print(f"Não há mais vértices para explorar a partir do vértice {current_vertex}, voltando...")
        if self.path:
            # Remove o vértice atual da pilha (volta para o último vértice)
            self.path.pop()
            last_visited =self.path.pop()
            print(f"Voltando ao vértice {last_visited}...")
            #print(f"Estado atual da pilha: {self.path}")

            # Envia o comando de volta para o último vértice visitado
            move_command = f"ir: {last_visited}"
            
            # Verifica se o comando de movimento está correto
            print(f"Enviando comando de movimento: {move_command}")
            
            try:
                await ws.send(move_command)
                await self.explore_maze( ws, last_visited)
            except Exception as e:
                print(f"Erro ao enviar comando de movimento: {e}")
        return  # Retorna quando não há mais vértices para explorar (backtracking)



    def update_maze_data(self, vertex, vertex_type, adjacent):
        self.graph[vertex] = adjacent
        self.types[vertex] = vertex_type
        self.visited.append(vertex)
        self.path.append(vertex)
        
        if vertex_type == 1:
            self.entry_vertex = vertex
        elif vertex_type == 2:
            self.exit_vertex = vertex

    def should_stop_exploration(self):
        #return self.path == []
        return self.exit_vertex is not None

    def find_next_vertex(self, adjacent):
        return next((v for v in adjacent if v not in self.visited), None)

    def print_exit_and_path(self):
        print("caminho:", self.visited)
        print(f"\nSaida encontrada:: {self.exit_vertex}")
        if self.entry_vertex is not None and self.exit_vertex is not None:
            shortest_path = bidirectional_search(self.graph, self.entry_vertex, self.exit_vertex)
            if shortest_path:
                print("Shortest path from entry to exit:")
                print(" → ".join(map(str, shortest_path)))
                print(f"Path length: {len(shortest_path)} vertices")

    async def finalize_maze(self):
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, submit_maze_solution, self.path
            )
            print("resposta aceita")
        except Exception as e:
            print(f"Falha ao enviar resposta: {e}")

    async def display_scoreboard(self):
        try:
            scoreboard = await asyncio.get_event_loop().run_in_executor(
                None, get_scoreboard
            )
            print("\nScoreboard:")
            for group in scoreboard:
                print(f"\nGroup: {group['grupo']}")
                for maze in group['labirintos']:
                    print(f"  Maze: {maze['labirinto']}, "
                          f"Steps: {maze['passos']}, "
                          f"Time: {maze['exploracao']}s")
        except Exception as e:
            print(f"Failed to display scoreboard: {e}")

def interpretar_resposta_bruta(resposta):
    try:
        partes = resposta.split(", Adjacentes")
        if len(partes) < 2:
            raise ValueError("Formato inesperado da resposta. Não encontrado o campo 'Adjacentes'.")
        
        vertice_info = partes[0].split(", ")
        vertice_atual = int(vertice_info[0].split(":")[1].strip())
        tipo = int(vertice_info[1].split(":")[1].strip())
        
        adjacentes_str = partes[1].split(":")[1].strip()
        adjacentes = [vertice for vertice, peso in eval(adjacentes_str)]  # Avalia a string adjacente e converte
        
        return vertice_atual, tipo, adjacentes
    except Exception as e:
        print(f"Erro ao interpretar a resposta bruta: {e}")
        return None, None, []  # Garantindo que sempre retornamos três valores válidos