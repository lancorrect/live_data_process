import json
import pathlib
from pathlib import Path
from pydub import AudioSegment
import re
from tqdm import tqdm

basedir = "your dir"
output_basedir = "your dir"

def segment(time_tag, set_tag, set_num=5000):
    dataset_dir = Path('output')/time_tag/'transcripts'/set_tag
    output_dir = Path(output_basedir)/time_tag/set_tag

    for industry_dir in dataset_dir.iterdir():
        print(f'Processing {industry_dir.name}\'s {set_tag} data.')
        folder_name = 'd0001'
        folder_num = 0
        industry = industry_dir.name
        output_folder_dir = output_dir/industry/folder_name
        output_folder_dir.mkdir(parents=True, exist_ok=True)
        for json_file in tqdm(industry_dir.rglob('*.json')):
            sec_id = json_file.parent.parent.name
            live_id = json_file.parent.name
            wav_name = json_file.stem
            wav_dir = Path(basedir)/time_tag/sec_id/live_id/wav_name
            speech = AudioSegment.from_wav(str(wav_dir)+'.wav')
            
            with open(json_file, 'r') as f:
                segment_info = json.load(f)
                f.close()
            for info in segment_info:
                start_ms = info['start_ms']
                end_ms = info['end_ms']
                speech_unit = speech[start_ms:end_ms]
                wav_name_new = wav_name+'_'+'0'*(6-len(str(start_ms)))+str(start_ms)\
                                        +'_'+'0'*(6-len(str(end_ms)))+str(end_ms)+'.wav'
                segment_dir = output_folder_dir / Path(wav_name_new)
                speech_unit.export(segment_dir, format="wav")

                sentence = info['sentence']
                sentence=re.sub(r'[\s+\.\!\/_,$%^*(+\"\'):-\\|]+|[+——()?【】“”！，。？、~@#￥%……&*（）：-]+', '', sentence)
                sentence_name = wav_name+'_'+'0'*(6-len(str(start_ms)))+str(start_ms)\
                                            +'_'+'0'*(6-len(str(end_ms)))+str(end_ms)+'_tarsocial'+'.txt'
                sentence_dir = output_folder_dir / Path(sentence_name)
                with open(sentence_dir, 'w') as f:
                    f.write(sentence)
                    f.close()

                folder_num += 1
                if folder_num >= set_num:
                    folder_id = int(folder_name[1:]) + 1
                    folder_name = 'd' + '0'*(4-len(str(folder_id))) + str(folder_id)
                    output_folder_dir = output_dir/industry/folder_name
                    output_folder_dir.mkdir(parents=True, exist_ok=True)
                    folder_num = 0


def statistic(time_tag, set_tag):
    industry_wav_num_dict = {}
    dataset_dir = Path('output')/time_tag/'transcripts'/set_tag
    output_dir = Path(output_basedir)/time_tag/set_tag

    for industry_dir in dataset_dir.iterdir():
        industry = industry_dir.name
        wav_num = 0
        for json_file in industry_dir.rglob("*.json"):
            with open(json_file, 'r') as f:
                segment_info = json.load(f)
                f.close()
            wav_num += len(segment_info)
        industry_wav_num_dict.setdefault(industry, wav_num)
    
    for industry_dir in output_dir.iterdir():
        wav_num = len([d for d in industry_dir.rglob("*.wav")])
        assert wav_num == industry_wav_num_dict[industry_dir.name], f"{industry.name}\'s number is wrong"
    
    print("statistic situation: ", industry_wav_num_dict)

if __name__ == "__main__":
    time_tag = "27_Jun_2023_12"

    segment(time_tag, 'train')
    statistic(time_tag, 'train')