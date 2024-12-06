from collections import deque

def bidirectional_search(graph, start, goal):
    if start not in graph or goal not in graph:
        return None
        
    # Initialize queues for both directions
    queue_start = deque([start])
    queue_goal = deque([goal])
    
    # Track visited vertices and their parents
    visited_start = {start: None}
    visited_goal = {goal: None}
    
    while queue_start and queue_goal:
        # Expand from start
        current_start = queue_start.popleft()
        for neighbor in graph[current_start]:
            if neighbor not in visited_start:
                visited_start[neighbor] = current_start
                queue_start.append(neighbor)
                if neighbor in visited_goal:
                    return reconstruct_path(visited_start, visited_goal, neighbor)
        
        # Expand from goal
        current_goal = queue_goal.popleft()
        for neighbor in graph[current_goal]:
            if neighbor not in visited_goal:
                visited_goal[neighbor] = current_goal
                queue_goal.append(neighbor)
                if neighbor in visited_start:
                    return reconstruct_path(visited_start, visited_goal, neighbor)
    
    return None

def reconstruct_path(visited_start, visited_goal, meeting_point):
    path = []
    
    # Path from start to meeting point
    current = meeting_point
    while current is not None:
        path.insert(0, current)
        current = visited_start[current]
    
    # Path from meeting point to goal
    current = visited_goal[meeting_point]
    while current is not None:
        path.append(current)
        current = visited_goal[current]
    
    return path