class MazeValidator:
    @staticmethod
    def validate_vertex(vertex, vertex_type, adjacent):
        if not isinstance(vertex, int) or vertex < 0:
            raise ValueError(f"Invalid vertex number: {vertex}")
        
        if vertex_type not in [0, 1, 2]:
            raise ValueError(f"Invalid vertex type: {vertex_type}")
        
        if not isinstance(adjacent, list) or not all(isinstance(v, int) and v >= 0 for v in adjacent):
            raise ValueError("Invalid adjacent vertices format")
        
        return True
    
    @staticmethod
    def validate_path(path, graph):
        if not path:
            raise ValueError("Path must be non-empty")
            
        for i in range(len(path) - 1):
            current = path[i]
            next_vertex = path[i + 1]
            if next_vertex not in graph[current]:
                raise ValueError(f"Invalid path: vertex {current} not connected to {next_vertex}")
        
        return True