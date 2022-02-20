## MagicCodeGame-Solver
### ⚠️ Under Construction
#### `magiccode` compiler framework and problem solving agent for Magic Code levels!
------------------------------------------------------------------------------------
> I started to play this wonderful programming game from the Nintendo Switch online store. 
> Eventually, my friends and me would spend hours trying to build a solution, to no avail. Hence, I built this agent 
> and compiler framework.

![Magic code | Trailer (Nintendo Switch)](https://i.makeagif.com/media/2-20-2022/g1sj-v.gif)

## Usage:
---------
Run the following to build out the level definition file using:

```sh
magiccode --template level_1.py
```

Next, carefully study the layout of the map on screen and translate it into map coordinates. See the documentation
for various kinds of terrain kinds.

```python
#!/usr/bin/env python3
# level_1.py

from magic.elements import *
from magic.state import *
from magic.ai import *

...
```

Finally, run the solver utility. This compiles the instructions from your source into a full
representation of the Magic Code game state and execution logic. It will generate a solution
for you if you're stuck!

```sh
magiccode --solve level_1.py
```

> *If you're seeing errors, consider opening a Bug Report. But before doing that, it might be appropriate to double check your map layout.*

If you want to see more, check out the `/examples` folder. 

