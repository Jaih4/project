import requests
from config import API_BASE_URL, LABIRINTO_ID, GRUPO_ID

def submit_maze_solution(path):
    try:
        response = requests.post(
            f"{API_BASE_URL}/resposta",
            json={
                "labirinto": LABIRINTO_ID,
                "grupo": GRUPO_ID,
                "vertices": path
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error no envio da resposta: {e}")
        raise

def get_scoreboard():
    try:
        response = requests.get(f"{API_BASE_URL}/placar")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching scoreboard: {e}")
        raise