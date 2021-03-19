#%%
import re


sentence_patten = "[^\\.]*\\."


def extract_citation_info(txt_path: str, title: str):
    with open(txt_path) as f:
        text_ori = f.read()
    text = text_ori.replace("\n", "")

    words = re.findall(r"\w+", title)

    pattern = "\\[[^\\[\\]]*\\][^\\[\\]]*" + "\\W*".join(words)

    citation = re.search(pattern, text, re.I | re.U).group()

    print(citation)

    citation_idx = re.findall("\\[[^\\d]*(\\d*)[^\\d]*\\]", citation)[0]

    print(
        re.findall(
            sentence_patten
            + "[^\\.]*"
            + "\\[[^\\[\\]]*"
            + citation_idx
            + "[^\\[\\]]*\\]"
            + sentence_patten
            + sentence_patten,
            text,
        )
    )


extract_citation_info(
    "c.txt", "A novel consistent random forest framework: Bernoulli random forests"
)

# %%
txt_path = "d.txt"
title = "A novel consistent random forest framework: Bernoulli random forests"


def extract_citation_info2(txt_path: str, title: str):
    with open(txt_path) as f:
        text_ori = f.read()
    text = text_ori.replace("\n", "")

    words = re.findall(r"\w+", title)

    pattern = "\\d+\\.[^\\d]*" + "\\W*".join(words)

    citation = re.search(pattern, text, re.I | re.U).group()

    print(citation)

    citation_idx = re.findall("(\\d+)\\.", citation)[0]

    print(
        re.findall(
            sentence_patten
            + "[^\\.]*"
            + "\\[[^\\[\\]]*"
            + citation_idx
            + "[^\\[\\]]*\\]"
            + sentence_patten
            + sentence_patten,
            text,
        )
    )


extract_citation_info2(
    txt_path="d.txt",
    title="A novel consistent random forest framework: Bernoulli random forests",
)

# %%
citation = re.search(pattern, text, re.I | re.U).group()
# %%
citation_idx = re.findall("(\\d+)\\.", citation)[0]
citation_idx
# %%
print(
    re.findall(
        sentence_patten
        + "[^\\.]*"
        + "\\[[^\\[\\]]*"
        + citation_idx
        + "[^\\[\\]]*\\]"
        + sentence_patten
        + sentence_patten,
        text,
    )
)

# %%

txt_path = "e.txt"
title = "On the Convergence and Robustness of Adversarial Training"
with open(txt_path) as f:
    text_ori = f.read()
text = text_ori.replace("\n", "")
words = re.findall(r"\w+", title)
pattern = "\\W*".join(words) + ".*?\\d{4}\\."
citation = re.search(pattern, text, re.I | re.U).group()
# %%
citation
# %%

# %%
re.findall("\\(Wang[^\\(\\)]*?, 2019\\)", text)
# %%
