#!/usr/bin/env python3
import os
import sys
import argparse
import time
import subprocess
import shutil
import requests
from elasticsearch import Elasticsearch

date = time.strftime("%Y-%m-%d_%H:%M")
ext = '.json'
complete_file = date + ext
elasticsearch_host = Elasticsearch()

parser = argparse.ArgumentParser(description="Port crawling script")
parser.add_argument('--masscan_bin', help='path to masscan', default='/usr/bin/masscan')
parser.add_argument('--masscan_rate', help='masscan rate', default='10000000')
parser.add_argument('--masscan_args', help='additional masscan args', nargs='+')
parser.add_argument('--chrome_bin', help='path to google-chrome', default='/usr/bin/chromium-browser')
parser.add_argument('--jq_bin', help='path to jq', default='/usr/bin/jq')
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
            es.index(index=index_name, doc_type='scan', id=i, body=line)
            i=i+1
    f.closed


def scanner(masscan, ip, ports, masscan_rate, masscan_args):
    ip = ' '.join(ip)
    ports = ','.join(ports)
    if masscan_args:
        masscan_args = ' '.join(masscan_args)
        os.system(masscan + ' ' + ip + ' -p' + str(ports) + ' --rate ' + str(masscan_rate) + ' --banners -oJ ' + complete_file + ' ' + masscan_args)
    else:
        os.system(masscan + ' ' + ip + ' -p' + str(ports) + ' --rate ' + str(masscan_rate) + ' --banners -oJ ' + complete_file)
    os.system("sed '1d; $d' " + complete_file + " > " + date)
    os.system("sed 's/.$//' " + date + " > " + complete_file)
    os.system("sed -i '/^$/d' " + complete_file)
    os.system("sed -i 's/$/ }/' " + complete_file) 
    try:
        os.remove(date)
    except FileNotFoundError:
        pass


def main():
    scanner(args.masscan_bin, args.ip, args.ports, args.masscan_rate, args.masscan_args)
    if not args.test:
        es_uploader(date, complete_file, elasticsearch_host, args.index_prefix)
    if not args.test:
        try:
            os.remove(complete_file)
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    main()
