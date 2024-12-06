from uuid import UUID
GRUPO_ID = "f2a59f75-7f87-48d1-b9c7-39b2d5387ce8"
LABIRINTO_ID = 1
labirinto_id_hex = hex(LABIRINTO_ID)[2:] 
WEBSOCKET_URL = f"ws://localhost:8000/ws/{GRUPO_ID}/{LABIRINTO_ID}"
API_BASE_URL = "http://localhost:8000"