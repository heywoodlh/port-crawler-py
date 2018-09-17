#!/usr/bin/env python3
import os
import sys
import argparse
import time
import subprocess
import shutil
import requests
from elasticsearch import Elasticsearch


parser = argparse.ArgumentParser(description="Port crawling script")
parser.add_argument('--masscan_rate', help='masscan rate', default='1000')
parser.add_argument('--masscan_args', help='additional masscan args', nargs='+')
parser.add_argument('--ip', help='IP(s) to scan', nargs='+', required='True')
parser.add_argument('-p', '--ports', help='Port(s) to scan', nargs='+', required='True')
parser.add_argument('-i', '--index_prefix', help='Prefix of index', default='portscan')
parser.add_argument('--test', help='do not upload for testing', action="store_true")

args = parser.parse_args()


def es_uploader(date, complete_file, es, index_prefix):
    i=0
    docs ={}
    index_name = index_prefix + date
    with open(complete_file) as f:
        for line in f:
            line = line.rstrip('\n')
            if line == '[' or line == ',' or line == ']':
                pass
            else:
                es.index(index=index_name, doc_type='scan', id=i, body=line)
            i=i+1
    f.closed


def scanner(ip, ports, masscan_rate, masscan_args):
    ip = ','.join(ip)
    ports = ','.join(ports)
    if masscan_args:
        masscan_args = ' '.join(masscan_args)
        subprocess.run(['masscan', str(ip),'-p', str(ports), '--rate', str(masscan_rate), '--banners', '-oJ', complete_file, masscan_args])
    else:
        subprocess.run(['masscan', str(ip),'-p', str(ports), '--rate', str(masscan_rate), '--banners', '-oJ', complete_file])
    #subprocess.run(['sed', '''1d; $d''', str(complete_file), '>', str(date)])
    #subprocess.run(['sed', '''s/.$//''', str(date), '>', str(complete_file)])
    #subprocess.run(['sed', '-i', '''/^$/d''', str(complete_file)])
    #subprocess.run(['sed', '-i', '''s/$/ }/''', str(complete_file)]) 
    try:
        os.remove(date)
    except FileNotFoundError:
        pass


def main():
    global date
    date = time.strftime("%Y-%m-%d_%H:%M")
    ext = '.json'
    global complete_file
    complete_file = date + ext
    elasticsearch_host = Elasticsearch()
    scanner(args.ip, args.ports, args.masscan_rate, args.masscan_args)
    if not args.test:
        es_uploader(date, complete_file, elasticsearch_host, args.index_prefix)
    if not args.test:
        try:
            os.remove(complete_file)
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    main()
