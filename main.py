import asyncio
from maze_explorer import MazeExplorer

async def main():
    try:
        explorer = MazeExplorer()
        await explorer.explore()
    except Exception as e:
        print(f"Main execution error: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())