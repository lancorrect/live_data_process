import urllib.request as request
from urllib.parse import urljoin
import json
import os
from pathlib import Path
import time
from shutil import rmtree
from ffmpy3 import FFmpeg
from threading import Thread
import argparse

url_head = 'your url'

def Download_Flvs(url, output_dir):
    flv_html = request.urlopen(url).read()
    flv_info = json.loads(flv_html)

    for info in flv_info:
        flv_id = info['name']
        flv_dir = output_dir / Path(flv_id)
        request.urlretrieve(url+flv_id, flv_dir)
        wav_dir = output_dir / Path(flv_dir.name.replace('flv', 'wav'))
        ff = FFmpeg(inputs={str(flv_dir):None}, 
                    outputs={str(wav_dir):'-vn -ar 16000 -ac 1 -ab 192 -f wav'})
        # print(ff.cmd)
        ff.run()
        flv_dir.unlink()

def Download_Flvs_by_display_id(url, output_dir):
    display_id_html = request.urlopen(url).read()
    display_id_info = json.loads(display_id_html)

    for info in display_id_info:
        display_id = info['name']
        date_anchor_display_dir = output_dir / Path(display_id)
        if not date_anchor_display_dir.exists():
            date_anchor_display_dir.mkdir()
        Download_Flvs(url+display_id+'/', date_anchor_display_dir)

def Download_Flvs_by_anchors(anchors_info, date_before, date_set, output_dir):

    for info in anchors_info:
        upload_time = info['mtime']
        date_str = upload_time.split(',')[1]  #  e.g. 28 Jun 2023 00:29:22 GMT
        date = time.strptime(date_str, " %d %b %Y %H:%M:%S GMT")
        
        if date<=date_set and date>=date_before:
            anchor_id = info['name']
            date_anchor_dir = output_dir / Path(anchor_id)
            if not date_anchor_dir.exists():
                date_anchor_dir.mkdir()
            Download_Flvs_by_display_id(url_head+anchor_id+'/', date_anchor_dir)

def partition_anchors(url, threads_num):
    anchors_html = request.urlopen(url).read()
    anchors_info = json.loads(anchors_html)

    anchors_threads = []
    step = len(anchors_info) // threads_num
    index = 0
    while index < threads_num-1:
        anchors_threads.append(anchors_info[step*index:step*(index+1)])
        index += 1
    anchors_threads.append(anchors_info[step*index:])
    
    return anchors_threads

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download flvs and contert them into wavs")
    parser.add_argument("--date_set_str", type=str, default='27_Jun_2023_14', help='the specified date')
    parser.add_argument("--threads", type=int, default=10, help='the number of threads')
    parser.add_argument("--flvs_dir", type=str, default='your dataset', help='output directory')
    args = parser.parse_args()
    
    date_min_str = ' 27 Jun 2023 09:43:55 GMT'
    date_max_str = ' 28 Jun 2023 11:42:21 GMT'
    date_min = time.strptime(date_min_str, " %d %b %Y %H:%M:%S GMT")
    date_max = time.strptime(date_max_str, " %d %b %Y %H:%M:%S GMT")
    
    date_set_str = args.date_set_str
    date_set = time.strptime(date_set_str, "%d_%b_%Y_%H")
    assert date_set>=date_min and date_set<=date_max, f"The specified date {date_set_str} is out of scope."

    if not Path(args.flvs_dir).exists():
        Path(args.flvs_dir).mkdir()
    
    date_downloaded_list = list(time.strptime(d.name, "%d_%b_%Y_%H") for d in Path(args.flvs_dir).iterdir())
    if date_downloaded_list:
        date_before = sorted(date_downloaded_list)[-1]
    else:
        date_before = date_min

    date_dir = Path(args.flvs_dir) / Path(date_set_str)
    if date_dir.exists():
        rmtree(date_dir)        
    date_dir.mkdir()
    
    threads_num = args.threads
    anchors_threads = partition_anchors(url_head, threads_num)
    # Download_Flvs_by_anchors(anchors_threads[0], date_before, date_set, date_dir)
    l_tasks = []
    for i in range(threads_num):
        th = Thread(target=Download_Flvs_by_anchors, args=(anchors_threads[i], date_before, date_set, date_dir))
        th.start()
        l_tasks.append(th)
        time.sleep(1)
    for th in l_tasks:
        th.join()