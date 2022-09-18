from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

def pathfind(board: "list[list[bool]]", frompos: "tuple[int, int]", topos: "tuple[int, int]") -> "list[tuple[int, int]] | None":
	"""Finds the path from a point to a different point. Return None if no path is found."""
	# Create a grid from the board.
	matrix = [[1 if state else 0 for state in row] for row in board]
	grid = Grid(matrix=matrix)
	# Start and end nodes
	try:
		start = grid.node(int(frompos[0]), int(frompos[1]))
		end = grid.node(int(topos[0]), int(topos[1]))
	except IndexError:
		print(f"OUT OF BOUNDS: {frompos} -> {topos}")
		return None
	# Find the path.
	finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
	path, runs = finder.find_path(start, end, grid)
	# Return the path.
	if len(path) > 0:
		return path
