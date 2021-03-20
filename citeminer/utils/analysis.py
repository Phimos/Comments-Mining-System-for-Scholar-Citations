import os
import json


def collect_failed_data(metadata_dir: str) -> None:
    success_cnt = 0
    failed_cnt = 0

    failed_eprint_cnt = 0
    failed_nolink_cnt = 0
    failed_puburl_only_cnt = 0

    ieeeexplore_cnt = 0
    researchgate_cnt = 0
    sciencedirect_cnt = 0
    invalid_cnt = 0
    others_cnt = 0

    tmp = []

    for author in os.listdir(metadata_dir):
        author_path = os.path.join(metadata_dir, author, "publications")
        for pub in os.listdir(author_path):
            pub_path = os.path.join(author_path, pub, "cited")
            for cpub in os.listdir(pub_path):
                with open(os.path.join(pub_path, cpub)) as infile:
                    info = json.load(infile)

                if "saved" not in info.keys():
                    continue

                if info["saved"] == "success":
                    success_cnt += 1
                    continue

                else:
                    failed_cnt += 1
                    if "eprint_url" in info.keys():
                        failed_eprint_cnt += 1

                        if "ieeexplore" in info["eprint_url"]:
                            ieeeexplore_cnt += 1
                            # print(info["eprint_url"])
                        elif "researchgate" in info["eprint_url"]:
                            researchgate_cnt += 1
                        elif "sciencedirect" in info["eprint_url"]:
                            # print(info["eprint_url"])
                            sciencedirect_cnt += 1
                        elif "/scholar?" in info["eprint_url"]:
                            invalid_cnt += 1
                        else:
                            # tmp.append(info["eprint_url"])
                            others_cnt += 1

                    if "eprint_url" not in info.keys() and "pub_url" not in info.keys():
                        failed_nolink_cnt += 1

                    if "eprint_url" not in info.keys() and "pub_url" in info.keys():
                        tmp.append(info["pub_url"])
                        failed_puburl_only_cnt += 1

    # sorted(tmp)
    # for i in sorted(tmp):
    #    print(i)

    # report failed info
    print("=" * 10 + "Failed Reason Analysis" + "=" * 10)
    print("[Success]: %d" % success_cnt)
    print("[Failed]: %d" % failed_cnt)
    print("[Failed Rate]: %.2f%%" % (100 * failed_cnt / (success_cnt + failed_cnt)))

    print("")

    print("[Contain Eprint URL]: %.2f%%" % (100 * failed_eprint_cnt / failed_cnt))
    print("[Only Pub URL]: %.2f%%" % (100 * failed_puburl_only_cnt / failed_cnt))
    print("[No Link]: %.2f%%" % (100 * failed_nolink_cnt / failed_cnt))

    print("")

    print("[IEEE]: %.2f%%" % (100 * ieeeexplore_cnt / failed_eprint_cnt))
    print("[ResearchGate]: %.2f%%" % (100 * researchgate_cnt / failed_eprint_cnt))
    print("[ScienceDirect]: %.2f%%" % (100 * sciencedirect_cnt / failed_eprint_cnt))
    print("[Invalid]: %.2f%%" % (100 * invalid_cnt / failed_eprint_cnt))
    print("[Others]: %.2f%%" % (100 * others_cnt / failed_eprint_cnt))
