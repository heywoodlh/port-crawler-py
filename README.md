## Quick Installation on Ubuntu:

### Run the install.sh script:

The `install.sh` script has been provided to simplify installing dependencies.

```
sudo chown -R "$USER:$USER" /opt
cd /opt
git clone https://github.com/heywoodlh/Port-Crawler
cd Port-Crawler
sudo ./install.sh
```


## Running port-crawler.py

Help message:


```
❯ ./port-crawler.py --help
usage: port-crawler.py [-h] [--masscan_bin MASSCAN_BIN]
                       [--masscan_rate MASSCAN_RATE]
                       [--masscan_args MASSCAN_ARGS [MASSCAN_ARGS ...]]
                       [--jsonpyes_bin JSONPYES_BIN] [--chrome_bin CHROME_BIN]
                       [--jq_bin JQ_BIN] [--elasticsearch_host HOST] --ip IP
                       [IP ...] -p PORTS [PORTS ...] -i INDEX_PREFIX [-s]
                       [--dir DIR] [--blank_master BLANK.PNG]
                       [-g GALLERY.HTML] [--devicify] [--test]

Port crawling script

optional arguments:
  -h, --help            show this help message and exit
  --masscan_bin MASSCAN_BIN
                        path to masscan
  --masscan_rate MASSCAN_RATE
                        masscan rate
  --masscan_args MASSCAN_ARGS [MASSCAN_ARGS ...]
                        additional masscan args
  --jsonpyes_bin JSONPYES_BIN
                        path to jsonpyes
  --chrome_bin CHROME_BIN
                        path to google-chrome
  --jq_bin JQ_BIN       path to jq
  --elasticsearch_host HOST
                        elasticsearch host
  --ip IP [IP ...]      IP(s) to scan
  -p PORTS [PORTS ...], --ports PORTS [PORTS ...]
                        Port(s) to scan
  -i INDEX_PREFIX, --index_prefix INDEX_PREFIX
                        Prefix of index
  -s, --screenshot      take screenshots
  --dir DIR             screenshot dir
  --blank_master BLANK.PNG
                        undesired png(s) to compare screenshots to
  -g GALLERY.HTML, --gallery GALLERY.HTML
                        add gallery.html to screenshots directory
  --devicify            attempt to identify devices
  --test                do not upload for testing
```


All of the `*_bin` arguments can be bypassed if you used the `install.sh` script.


Example command:

```
sudo /opt/Port-Crawler-Py/port-crawler.py --masscan_rate 1000 --ip 192.168.1.10 192.168.1.50 --ports 80 443 --index_prefix portscans -s --devicify
```


If you enable screenshots, the default location on the server that they will be stored at will be `/opt/Port-Crawler-Py/screenshots`. If you'd like to view the screenshots in a web browser, install a web server and configure it to use the screenshots directory. The `gallery.html` file will be placed in the screenshots directory allowing you to use that file to view all the screenshots on a nice html page rendered in a web server (I.E. http://myscanner.com/screenshots/gallery.html).

