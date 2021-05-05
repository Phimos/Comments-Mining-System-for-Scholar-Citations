import json
import os
import re
from collections import Counter

import pandas as pd
import tableprint as tp


def collect_failed_data(metadata_dir: str = os.path.join("result", "metadata")) -> None:
    success_cnt = 0
    failed_cnt = 0

    failed_eprint_cnt = 0
    failed_without_eprint_cnt = 0

    eprint_urls = []
    pub_urls = []

    for author in os.listdir(metadata_dir):
        author_path = os.path.join(metadata_dir, author, "publications")
        for pub in os.listdir(author_path):
            pub_path = os.path.join(author_path, pub, "cited")
            for cpub in os.listdir(pub_path):
                with open(os.path.join(pub_path, cpub)) as infile:
                    info = json.load(infile)

                if "saved" not in info.keys():
                    continue

                #                if info["saved"] == "success":
                if os.path.exists(
                    os.path.join(
                        pub_path.replace("/metadata/", "/pdfs/"),
                        cpub.replace(".json", ".pdf"),
                    )
                ):
                    success_cnt += 1
                    continue

                else:
                    failed_cnt += 1
                    if "eprint_url" in info.keys():
                        failed_eprint_cnt += 1
                        eprint_urls.append(info["eprint_url"])
                        # print(info["eprint_url"])
                    else:
                        failed_without_eprint_cnt += 1
                    pub_urls.append(info["pub_url"])

    # report failed info
    status_table = pd.DataFrame(columns=["Status", "Count", "Percentage"])
    status_table = status_table.append(
        {
            "Status": "Success",
            "Count": success_cnt,
            "Percentage": "%.2f%%" % (100 * success_cnt / (success_cnt + failed_cnt)),
        },
        ignore_index=True,
    )
    status_table = status_table.append(
        {
            "Status": "Failed",
            "Count": failed_cnt,
            "Percentage": "%.2f%%" % (100 * failed_cnt / (success_cnt + failed_cnt)),
        },
        ignore_index=True,
    )
    status_table = status_table.append(
        {
            "Status": "Total",
            "Count": success_cnt + failed_cnt,
            "Percentage": "%.2f%%" % (100),
        },
        ignore_index=True,
    )
    print("Result Status Table".center(88))
    tp.dataframe(status_table, width=26)

    reason_table = pd.DataFrame(columns=["Contain Eprint URL", "Count", "Percentage"])
    reason_table = reason_table.append(
        {
            "Contain Eprint URL": "Yes",
            "Count": failed_eprint_cnt,
            "Percentage": "%.2f%%" % (100 * failed_eprint_cnt / failed_cnt),
        },
        ignore_index=True,
    )
    reason_table = reason_table.append(
        {
            "Contain Eprint URL": "No",
            "Count": failed_without_eprint_cnt,
            "Percentage": "%.2f%%" % (100 * failed_without_eprint_cnt / failed_cnt),
        },
        ignore_index=True,
    )
    reason_table = reason_table.append(
        {
            "Contain Eprint URL": "Total",
            "Count": failed_cnt,
            "Percentage": "%.2f%%" % (100),
        },
        ignore_index=True,
    )

    print("Eprint-URL Status Table".center(88))
    tp.dataframe(reason_table, width=26)

    eprint_url_table = count_link(eprint_urls)
    print("Eprint-URL Domain Table".center(88))
    tp.dataframe(eprint_url_table, width=26)

    pub_url_table = count_link(pub_urls)
    print("Pub-URL Domain Table".center(88))
    tp.dataframe(pub_url_table, width=26)


def count_link(linkages, drop_percent: float = 5):
    domains = []
    for link in linkages:
        try:
            domains.append(re.findall("https?://([^/]*)/", link)[0])
        except:
            pass

    df = pd.DataFrame(domains, columns=["Domain"])
    df = df.groupby("Domain").size().reset_index(name="Count")
    df = df.sort_values(by="Count", ascending=False)
    df["Percentage"] = df["Count"] / df["Count"].sum() * 100
    out = df[df["Percentage"] >= drop_percent]

    out = out.append(
        {
            "Domain": "Others",
            "Count": df[df["Percentage"] < drop_percent]["Count"].sum(),
            "Percentage": df[df["Percentage"] < drop_percent]["Percentage"].sum(),
        },
        ignore_index=True,
    )
    out = out.append(
        {
            "Domain": "Total",
            "Count": df["Count"].sum(),
            "Percentage": df["Percentage"].sum(),
        },
        ignore_index=True,
    )

    out["Percentage"] = out["Percentage"].apply(lambda x: "%.2f%%" % x)
    return out
