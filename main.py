import os
import requests
import pandas as pd
from tqdm import tqdm
from time import sleep

def get_ip_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        ips = [line.strip() for line in f]
    return ips

def ipinfoapi(ips:list, session):
    url = 'http://ip-api.com/batch'
    ips_dict = [{'query': ip, "fields": "city,country,countryCode,isp,org,as,query"} for ip in ips]
    sleep(3)
    try:
        with session.post(url, json=ips_dict) as resp:
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f'获取ip信息失败: {resp.status_code}, {resp.reason}')
                return None
    except Exception as e:
        print(f'requests error:{e}')
        return None

def get_ip_info(ips):
    ipsinfo = []
    url = 'http://ip-api.com/batch'
    
    with tqdm(total=len(ips)) as bar:
        bar.set_description(f"Processed IP: {len(ips)}")
        with requests.Session() as session:
            for i in range(0, len(ips), 100):
                count = min(i+100, len(ips))
                t = ipinfoapi(ips[i:i + 100], session)
                if t != None:
                    ipsinfo += t
                bar.update(100)

    return ipsinfo

def gatherip(port):
    cfiplistDir = "./ips/"

    filelist = os.listdir(cfiplistDir)
    file_port = [file for file in filelist if file.split("-")[2] == f"{port}.txt"]
    allips = []
    # output_file = f"ip-{port}.txt"
    for file in file_port:
        allips += get_ip_from_file(cfiplistDir + file)

    return list(set(allips))

def process_ipinfo(ipinfo, port):
    # df = pd.DataFrame(ipinfo)
    save_dir = f"./ip{port}/"

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    grouped = pd.DataFrame(ipinfo).groupby('countryCode')
    for countryCode, group in grouped:
        only_ip = group['query'].drop_duplicates()
        only_ip.to_csv(save_dir + countryCode + '.txt', header=None, index=False)

def main(port):
    ips = gatherip(port)
    print(f"Total ips: {len(ips)}")
    ipinfo = get_ip_info(ips)
    process_ipinfo(ipinfo, port)

if __name__ == "__main__":
    main(443)
    print("Done!")
