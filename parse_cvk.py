import urllib3
import bs4
import re
import pandas as pd
import time
import numpy as np
from tqdm import tqdm
import argparse


def load_district_list(root_url: str, http: urllib3.PoolManager):
    district_url = "{0}/wp335pt001f01=720.html".format(root_url)
    req = http.request("GET", district_url)
    district_refs = extract_district_refs(root_url, req.data)
    return district_refs


def extract_district_refs(root_url, dictricts_html):
    def get_district_id(ref_str):
        match = re.search(r"=(\d{1,3}).html", ref_str)
        return match.group(1)

    soup = bs4.BeautifulSoup(dictricts_html)
    ref_a_tags = soup.find_all("a", attrs={"class": "a1"}, string=re.compile("^\d{1,3}$"))
    district_refs = [(get_district_id(a_tag["href"]), "{0}/{1}".format(root_url, a_tag["href"])) for a_tag in ref_a_tags]
    return district_refs


def load_district_data(district_url, http):
    req = http.request("GET", district_url)
    match = re.search(r"<table.*/table>", req.data.decode(encoding="cp1251").replace("\n", " "))
    table_html = match.group(0)
    district_df = pd.read_html(table_html)
    return district_df[0]


def save_districts_info(save_folder_path, district_id_url_pairs, http):
    for id, durl in tqdm(district_id_url_pairs):
        time.sleep(np.random.rand() * 3 + 0.7)
        district_df = load_district_data(durl, http)
        district_df["ТВО"] = np.ones(district_df.shape[0], dtype="int")*int(id)
        district_df.to_csv("{0}/{1}.csv".format(save_folder_path, id))


def load_results(save_folder_path):
    root_url = "https://www.cvk.gov.ua/pls/vp2019"
    http = urllib3.PoolManager()
    district_refs = load_district_list(root_url, http)
    save_districts_info(save_folder_path, district_refs, http)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load 2019 president election results from https://www.cvk.gov.ua")
    parser.add_argument("save_folder", type=str, help="Path for saving result data files.")
    args = parser.parse_args()

    load_results(args.save_folder)
