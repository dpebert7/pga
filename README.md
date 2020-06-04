## pga
*Postgame analysis for Acquire board game*

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dpebert7/pga/master?filepath=Main.ipynb)


### Example
```python
from pga import pga
sLog = """
...
...
...
"""
pga(sLog.splitlines())
```

Output:
```
Companies Formed:
{'afropop': 5, 'scarbinger': 5, 'TacoBobby': 2, 'WilyWhippoorwill': 1, 'VeryStableGenius': 1}

Bonus Money:
{'afropop': 18500, 'scarbinger': 22300, 'TacoBobby': 2000, 'WilyWhippoorwill': 7300, 'VeryStableGenius': 17500}

Final net worth:
{'afropop': '45900', 'scarbinger': '40800', 'TacoBobby': '22000', 'WilyWhippoorwill': '26800', 'VeryStableGenius': '23700'}

Merging Tiles Played:
{'afropop': 2, 'scarbinger': 2, 'TacoBobby': 2, 'WilyWhippoorwill': 3, 'VeryStableGenius': 1}
```





