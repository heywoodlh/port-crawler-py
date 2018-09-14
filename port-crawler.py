#!/usr/bin/env python3
import os
import sys
import argparse
import time
import subprocess
import shutil
import requests

web_ports = 80, 81, 8080


parser = argparse.ArgumentParser(description="Port crawling script")
parser.add_argument('--masscan_bin', help='path to masscan', default='/usr/bin/masscan')
parser.add_argument('--masscan_rate', help='masscan rate', default='10000000')
parser.add_argument('--masscan_args', help='additional masscan args', nargs='+')
parser.add_argument('--jsonpyes_bin', help='path to jsonpyes', default='/usr/local/bin/jsonpyes')
parser.add_argument('--chrome_bin', help='path to google-chrome', default='/usr/bin/chromium-browser')
parser.add_argument('--jq_bin', help='path to jq', default='/usr/bin/jq')
parser.add_argument('--elasticsearch_host', help='elasticsearch host', default='http://localhost:9200', metavar='HOST')
parser.add_argument('--ip', help='IP(s) to scan', nargs='+', required='True')
parser.add_argument('-p', '--ports', help='Port(s) to scan', nargs='+', required='True')
parser.add_argument('-i', '--index_prefix', help='Prefix of index', required='True')
parser.add_argument('-s', '--screenshot', help='take screenshots', action="store_true")
parser.add_argument('--dir', help='screenshot dir', default='./screenshots', metavar='DIR')
parser.add_argument('--blank_master', help='undesired png(s) to compare screenshots to', metavar='BLANK.PNG', default='./blank-master.png')
parser.add_argument('-g', '--gallery', help='add gallery.html to screenshots directory', metavar='GALLERY.HTML')
parser.add_argument('--devicify', help='attempt to identify devices', action="store_true")
parser.add_argument('--test', help='do not upload for testing', action="store_true")

args = parser.parse_args()

if args.devicify:
    from devices import *
    from bs4 import BeautifulSoup


date = time.strftime("%Y-%m-%d_%H:%M")
ext = '.json'
complete_file = date + ext



def es_uploader(jsonpyes, elasticsearch, index_prefix):
    os.system(jsonpyes + ' --data ' + complete_file + ' --bulk ' + elasticsearch + ' --import --index ' + index_prefix + date + ' --type scan ' + '--check --thread 8') 


def scanner(masscan, ip, ports, masscan_rate, jsonpyes, masscan_args):
    ip = ' '.join(ip)
    ports = ','.join(ports)
    if masscan_args:
        masscan_args = ' '.join(masscan_args)
        os.system(masscan + ' ' + ip + ' -p' + str(ports) + ' --rate ' + str(masscan_rate) + ' --banners -oJ ' + complete_file + ' ' + masscan_args)
    else:
        os.system(masscan + ' ' + ip + ' -p' + str(ports) + ' --rate ' + str(masscan_rate) + ' --banners -oJ ' + complete_file)
    os.system("sed '1d; $d' " + complete_file + " > " + date)
    os.system("sed 's/.$//' " + date + " > " + complete_file)
    try:
        os.remove(date)
    except FileNotFoundError:
        pass

    
def port_parser(scan_file, jq_bin):
    ports = subprocess.check_output("cat -s " + scan_file + " | " + jq_bin + " '.ports | map(.port)' | tr -d \[ | tr -d \] | sed 'N;/^\\n$/D;P;D;' | sed /^$/d", shell=True)
    ports_string = ports.decode("utf-8")
    ports = ports_string.split()
    return ports


def ip_parser(scan_file, jq_bin):
    ip_addresses = subprocess.check_output('cat -s ' + scan_file + ' | ' + jq_bin + ' \'.ip\' | tr -d \\"', shell=True)
    ip_addresses_string = ip_addresses.decode("utf-8")
    ip_addresses = ip_addresses_string.split()
    return ip_addresses


def url_parser(ports, ip_addresses):
    count = 0
    url_array = []
    global port_array
    port_array = []
    for ip in ip_addresses:
        port = ports[count]
        port_array.append(port)
        count += 1
        if port == 443:
            url = 'https://' + ip + ':' + str(port)
        else:
            url = 'http://' + ip + ':' + str(port)
        url_array.append(url)
    return url_array
 

def screenshot(chrome_bin, blank_master, complete_file, screenshots_dir):
    scan_file = complete_file
    ports = port_parser(scan_file, args.jq_bin)
    ip_addresses = ip_parser(scan_file, args.jq_bin)
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    urls = url_parser(ports, ip_addresses)
    count = 0
    global web_urls
    web_urls = []
    for url in urls:
        screenshot_file = ip_addresses[count] + '_' + port_array[count] + '.png'
        screenshot_file = screenshots_dir + '/' + screenshot_file
        if int(port_array[count]) in (web_ports):
            web_urls.append(url)
            if not os.path.isfile(screenshot_file):
                print('Taking screenshot of ' + url)
                os.system('timeout 5 ' + chrome_bin + ' --headless --no-sandbox --disable-gpu --screenshot=' + screenshot_file + ' --ignore-certificate-errors ' + url)
                os.system('[ "$( compare -metric rmse ' + screenshot_file + ' ' + blank_master + ' null: 2>&1 )" = "0 (0)" ] && rm ' + screenshot_file)
        count += 1
        

def cp_gallery(gallery, screenshots_dir):
    new_gallery = screenshots_dir + '/gallery.html'
    if not os.path.isfile(new_gallery):
        shutil.copyfile(gallery, new_gallery)
    

def web_devicify(host, dest_dir):
    ip = host
    try:
        response = requests.get(host)
        if response.status_code == 200:
            for device in device_list:
                device_file = dest_dir + '/' + device + '.txt'
                mydevices = device_list[device]
                if type(mydevices) is list:
                    for item in device_list[device]:
                        if str(item) in str(response.text):
                            print(ip + ' identified as ' + str(device_list[device]))
                            try:
                                open(device_file, 'r')
                            except IOError:
                                open(device_file, 'w')
                            if ip not in open(device_file).read():
                                with open(device_file, "a") as myfile:
                                    myfile.write(ip)
                else:
                    if str(device_list[device]) in str(response.text):
                        try:
                            open(device_file, 'r')
                        except IOError:
                            open(device_file, 'w')
                        if ip not in open(device_file).read():
                            with open(device_file, "a") as myfile:
                                myfile.write(ip)
    except requests.exceptions.SSLError:
        pass


def devicify(web_urls, screenshot_dir):
    for url in web_urls:
        web_dest = screenshot_dir + '/web'
        if not os.path.isdir(screenshot_dir):
            os.mkdir(screenshot_dir)
        if not os.path.isdir(web_dest):
            os.mkdir(web_dest)
        web_devicify(url, web_dest)


def main():
    scanner(args.masscan_bin, args.ip, args.ports, args.masscan_rate, args.jsonpyes_bin, args.masscan_args)
    if not args.test:
        es_uploader(args.jsonpyes_bin, args.elasticsearch_host, args.index_prefix)
    if args.screenshot:
        screenshot(args.chrome_bin, args.blank_master, complete_file, args.dir)
    if not args.test:
        try:
            os.remove(complete_file)
        except FileNotFoundError:
            pass
    if args.gallery:
        cp_gallery(args.gallery, args.dir)
    if args.devicify:
        devicify(web_urls, args.dir)


if __name__ == '__main__':
    main()
