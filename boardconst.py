# Block states
CHASM = 0
FLOOR = 1
WALL = 2
DOOR = 3
BOARDWALK = 4

# Blocks that prevent movement.
WALLBLOCKS = [CHASM, WALL]

# Blocks that you can move over.
FLOORBLOCKS = [FLOOR, DOOR, BOARDWALK]

# Blocks that you can see through.
SEETHROUGHBLOCKS = [CHASM, FLOOR, BOARDWALK]