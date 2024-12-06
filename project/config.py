from uuid import UUID
GRUPO_ID = "f68e8e5c-5646-44b7-b2c7-bce258e7c114"
LABIRINTO_ID = 1
labirinto_id_hex = hex(LABIRINTO_ID)[2:] 
WEBSOCKET_URL = f"ws://localhost:8000/ws/{GRUPO_ID}/{LABIRINTO_ID}"
API_BASE_URL = "http://localhost:8000"