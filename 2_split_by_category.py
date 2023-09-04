import os
import random
import json
import pathlib
import requests
from collections import defaultdict

random.seed(0)
basedir = "your dir"
category_url = "your url"


def split_by_category(tag):
    srcdir = pathlib.Path(basedir) / tag
    output_dir = pathlib.Path(f"output/{tag}/")
    output_dir.mkdir(parents=True, exist_ok=True)
    wavlist = sorted(srcdir.rglob("*.wav"))
    d = defaultdict(list)
    sec_id2cate = {}
    for wav in wavlist:
        room_id = wav.parent.name
        sec_id = wav.parent.parent.name
        if sec_id not in sec_id2cate:
            resp = requests.get(category_url + sec_id)
            cateName = resp.json()["data"]["cateName"]
            sec_id2cate[sec_id] = cateName
        cateName = sec_id2cate[sec_id]
        d[cateName].append({"sec_id": sec_id, "room_id": room_id, "wav": wav.as_posix()})
    info_json = output_dir / "all.json"
    with open(info_json.as_posix(), "w", encoding="utf-8")as f:
        json.dump(d, f, ensure_ascii=False, indent=4)
    for cate in d:
        print(cate, len(d[cate]))


def _split(items, num_test=2):
    all_sec_id_combine_room_id = set()
    l_train = []
    l_test = []
    for item in items:
        sec_id = item["sec_id"]
        room_id = item["room_id"]
        all_sec_id_combine_room_id.add(f"{sec_id}_{room_id}")
    test_sec_id_combine_room_id = []
    if len(all_sec_id_combine_room_id) > num_test:
        test_sec_id_combine_room_id = random.choices(list(all_sec_id_combine_room_id), k=num_test)
    for item in items:
        sec_id = item["sec_id"]
        room_id = item["room_id"]
        if f"{sec_id}_{room_id}" in test_sec_id_combine_room_id:
            l_test.append(item)
        else:
            l_train.append(item)
    return (l_train, l_test)


def split_train_and_test(tag):
    output_dir = pathlib.Path(f"output/{tag}/")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_json = pathlib.Path(f"output/{tag}/all.json")
    with open(all_json.as_posix(), "r", encoding="utf-8")as f:
        d = json.load(f)
    d_train = defaultdict(list)
    d_test = defaultdict(list)
    for cate in d:
        l_train, l_test = _split(d[cate])
        d_train[cate] = l_train
        d_test[cate] = l_test

    train_json = output_dir / "train.json"
    with open(train_json.as_posix(), "w", encoding="utf-8")as f:
        json.dump(d_train, f, ensure_ascii=False, indent=4)
    
    test_json = output_dir / "test.json"
    with open(test_json.as_posix(), "w", encoding="utf-8")as f:
        json.dump(d_test, f, ensure_ascii=False, indent=4)


def statistic_dataset(json_file):
    with open(json_file, "r", encoding="utf-8")as f:
        d = json.load(f)
    for cate in d:
        print(cate, len(d[cate]))
    

if __name__ == "__main__":
    tag = "27_Jun_2023_12"
    # split_by_category(tag)
    # split_train_and_test(tag)
    statistic_dataset(f"output/{tag}/train.json")
