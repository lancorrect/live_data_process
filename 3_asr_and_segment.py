import json
import time
import requests
import pathlib
from pathlib import Path
from threading import Thread
from queue import Queue
from pydub import AudioSegment
import re
from tqdm import tqdm


asr_url = "your asr api interface"


def upload_request(wav_path, url="http://localhost:8000"):
    url = f"{url}/upload"
    files = {"content": open(wav_path, "rb")}
    resp = requests.post(url, files=files)
    return resp


def get_result_request(task_id, url="http://localhost:8000"):
    url = f"{url}/getResult"
    data = {"task_id": task_id}
    resp = requests.post(url, json=data)
    return resp


def upload_task(q_upload, q_query):
    while not q_upload.empty():
        cate, item = q_upload.get()
        wav = item["wav"]
        max_retry_times = 10
        for _ in range(max_retry_times):
            try:
                resp = upload_request(wav, asr_url)
                if resp.status_code == 200:
                    task_id = json.loads(resp.text)["task_id"]
                    q_query.put((cate, item, task_id))
                    break
            except Exception as e:
                print("upload error:", str(e))
            time.sleep(5)
        print("q_upload size:", q_upload.qsize())


def query_task(q_upload, q_query, write_dir):
    while True:
        if q_upload.empty() and q_query.empty():
            break
        if q_query.empty():
            time.sleep(5)
        else:
            print("q_query size:", q_query.qsize())
            cate, item, task_id = q_query.get()
            sec_id = item["sec_id"]
            room_id = item["room_id"]
            wav = item["wav"]
            utt = pathlib.Path(wav).stem
            max_retry_times = 30
            for _ in range(max_retry_times):
                try:
                    resp = get_result_request(task_id, asr_url)
                    if resp.status_code == 200:
                        obj = json.loads(resp.text)
                        result = obj["result"]
                        result = json.loads(result)
                        save_dir = write_dir / cate / sec_id/ room_id
                        save_dir.mkdir(parents=True, exist_ok=True)
                        save_path = save_dir / f"{utt}.json"
                        with open(save_path, "w", encoding="utf-8")as f:
                            json.dump(result, f, indent=4, ensure_ascii=False)
                        break
                except Exception as e:
                    print("error task_id:", task_id, str(e))
                time.sleep(5)
            


def run(json_file, time_tag, set_tag):
    write_dir = pathlib.Path("output") / time_tag / "transcripts" / set_tag
    with open(json_file, "r", encoding="utf-8")as f:
        d = json.load(f)
    for cate in d:
        if cate in ["服饰", "美食", "美妆", "室外运动", "鞋包", "智能家居"]:
            continue
        print(cate)
        items = d[cate]
        q_upload = Queue()
        q_query = Queue()
        for item in items:
            q_upload.put((cate, item))
        l_upload = []
        l_query = []
        for _ in range(5):
            l_upload.append(Thread(target=upload_task, args=(q_upload, q_query)))
        for t in l_upload:
            t.start()
        for _ in range(10):
            l_query.append(Thread(target=query_task, args=(q_upload, q_query, write_dir)))
        for t in l_query:
            t.start()
        for t in l_upload:
            t.join()
        for t in l_query:
            t.join()

if __name__ == "__main__":
    time_tag = "27_Jun_2023_12"

    train_json = f"output/{time_tag}/train.json"
    run(train_json, time_tag, "train")

    # test_json = f"output/{time_tag}/test.json"
    # run(test_json, time_tag, "test")