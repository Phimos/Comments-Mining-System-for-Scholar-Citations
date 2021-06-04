#%%
import random
import time

import requests

out = requests.get("https://api.semanticscholar.org/v1/author/1919541")
data = eval(
    out.text.replace("null", "None").replace("true", "True").replace("false", "False")
)
# %%
from tqdm import tqdm

cnt = 0
for paper in tqdm(data["papers"]):
    out = requests.get("https://api.semanticscholar.org/v1/paper/" + paper["paperId"])
    print(out)
    paper_data = eval(
        out.text.replace("null", "None")
        .replace("true", "True")
        .replace("false", "False")
    )
    citations2020 = [
        c for c in paper_data.get("citations", []) if c.get("year") == 2020
    ]
    time.sleep(random.uniform(3, 5))
    cnt += len(citations2020)
# %%
len([c for c in paper_data["citations"] if c.get("year") == 2020])
# %%
eval(out.text.replace("null", "None").replace("true", "True").replace("false", "False"))
# %%
paper_data["isOpenAccess"]
# %%
cnt
# %%
cnt
# %%
