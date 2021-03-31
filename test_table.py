#%%
import time

import numpy as np
import pandas as pd
import tableprint as tp
from numpy.lib.shape_base import column_stack

table = tp.TableContext(["a", "bbb", "ccc"])

df = pd.DataFrame([["aaa", "ccc"], ["d", "www"]], columns=["column1", "column2"])

tp.dataframe(df)


#%%

with tp.TableContext(["a", "bbb", "ccc"]) as t:
    for _ in range(10):
        time.sleep(0.1)
        t(
            np.random.randn(
                3,
            )
        )
