#%%
import re


#%%
f = open("c.txt")

# %%
lines = f.readlines()
# %%
lines
# %%
ff = f.read()
# %%
ff
# %%
text = ff.replace("\n", "")
# %%
text
# %%
title = "A novel consistent random forest framework: Bernoulli random forests"
# %%
words = re.findall(r"\w+", title)
# %%
help(re.search)

#%%
newtext = "odel  for  motion  estimation[J].  IET Computer Vision, 2019, 13(3):277-284. [17]  V.  Belagiannis,  S.  Amin,  M.  Andriluka,  et  al.  “3D  Pictorial  structures revisited:  multiple  human  pose  estimation,”  in  IEEE  Transactions  on Pattern Analysis and Machine Intelligence, Vol. 38, no. 10. pp. 736-742, 2016. [18]  C. Zhe, T. Simon, W. Shihien, et al. “OpenPose: Realtime Multi-person 2D  Pose  Estimation  Using  Part  Affinity  Fields,”  in  IEEE  Transactions on  Pattern  Analysis and Machine Intelligence.  Vol. 36,  no. 8. pp.  736-742, 2019. [19]  W.  Yisen,  X.  Shutao,  T.  Qingtao,  et  al.  “A  Novel  Consistent  Random Forest Framework: Bernoulli Random Forests"
# %%
pattern = "\\[[^\\[\\]]*\\][^\\[\\]]*" + "\\W*".join(words)
# %%
pattern
# %%
res = re.search(pattern, text, re.I | re.U).group()
# %%
idx = re.findall("\\[[^\\d]*(\\d*)[^\\d]*\\]", res)[0]

#%%
sentence_patten = "[^\\.]*\\."

# %%
ttext = "en the passenger's behavior and its optical flow vector is explained by demonstrating the optical flow  field  of  the  passenger's  different  behavior.  Third,  the application of the random forest classifier [19-20] is beneficial. This  paper  classifies "
# %%
for v in re.finditer("\\[[^\\[\\]]*" + idx + "[^\\[\\]]*\\]", text):
    print(v)
# %%
idx == "19"
# %%

re.findall(
    sentence_patten
    + "[^\\.]*"
    + "\\[[^\\[\\]]*"
    + idx
    + "[^\\[\\]]*\\]"
    + sentence_patten
    + sentence_patten,
    text,
)
# %%
idx = "1"
# %%
re.findall("\\[[^\\[\\]]*" + idx + "[^\\[\\]]*\\]" + sentence_patten, text)
# %%

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
    citation_idx = "1"

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
