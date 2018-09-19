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
parser.add_argument('-r', '--rate', help='masscan rate')
parser.add_argument('-c', '--config', help='masscan config file')
parser.add_argument('--ip', help='IP(s) to scan', nargs='+')
parser.add_argument('-p', '--ports', help='Port(s) to scan', nargs='+')
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


def scanner(ip, ports, masscan_rate, masscan_config):
    if masscan_config:
        subprocess.run(['masscan', '-c', masscan_config, '-oJ', complete_file])
    else:
        if not ip:
            print('"--ip" argument required')
            sys.exit(1)
        if not ports:
            print('"--ports" argument required')
            sys.exit(1)
        ip = ','.join(ip)
        ports = ','.join(ports)
        subprocess.run(['masscan', str(ip),'-p', str(ports), '--rate', str(masscan_rate), '--banners', '-oJ', complete_file])
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
    masscan_rate = args.rate
    masscan_config = args.config
    scanner(args.ip, args.ports, masscan_rate, masscan_config)
    if not args.test:
        es_uploader(date, complete_file, elasticsearch_host, args.index_prefix)
    if not args.test:
        try:
            os.remove(complete_file)
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    main()
