##Port-Crawler-Py

![alt text](images/port-crawler.png)



## Quick Installation on Ubuntu:

### Run the install.sh script:

The `install.sh` script has been provided to simplify installing dependencies.

```
sudo chown -R "$USER:$USER" /opt
cd /opt
git clone https://github.com/heywoodlh/Port-Crawler-Py
cd Port-Crawler-Py
```

Edit the first variable in `install.sh` `IP_OR_HOSTNAME` to equal the IP address or hostname that Kibana will be served on.

```
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


Example command (change the IP addresses and the ports if you'd like):

```
sudo /opt/Port-Crawler-Py/port-crawler.py --masscan_rate 1000 --ip 192.168.0.1 192.168.0.10 192.168.2.0/24 --ports 0-1024 3389 4786 3306 5432 1433 8080 11211 7001  --index_prefix portscans -s --devicify
```


Set the scan to repeat itself on a regular basis -- at 1:00 a.m. every day -- with a cronjob (`sudo crontab -e`), changing the IP addresses and ports as you'd like:

```
0 1 * * * /opt/Port-Crawler-Py/port-crawler.py --masscan_rate 1000 --ip 192.168.0.1 192.168.0.10 192.168.2.0/24 --ports 0-1024 3389 4786 3306 5432 1433 8080 11211 7001  --index_prefix portscans -s --devicify
```


*Note: If you enable screenshots, the default location on the server that they will be stored at will be `/opt/Port-Crawler-Py/screenshots`. If you'd like to view the screenshots in a web browser, install a web server and configure it to use the screenshots directory. The `gallery.html` file will be placed in the screenshots directory allowing you to use that file to view all the screenshots on a nice html page rendered in a web server (I.E. http://myscanner.com/screenshots/gallery.html).*


## Configuring Kibana:

### Access Kibana:

You can go to http://hostname:5601 of your server and access Kibana. 


### Set up an index pattern:

In Kibana go to Management > Index Patterns > Create index pattern.

If you used an index prefix of 'portscans' in `port-crawler.py` (or didn't set an index pattern explicitly), set the index pattern to be 'portscans\*'. 

*Note: Data must be in Elasticsearch prior to setting up the index pattern to verify it matches the data in Elasticsearch. So run `port-crawler.py` prior to setting up the index pattern.*


### Set up default visualizations and dashboard:

In this repository is a copy of a default Kibana dashboard called `kibana-export.json` and visualizations that can be used to visualize the results of `port-crawler.py`'s `masscan` results.

In order to import it go to Management > Saved Objects > Import. Download `kibana-export.json` to the machine that you are accessing the Kibana interface from and select `kibana-export.json` to import the dashboard and visualizations.


### Map the timestamp field to a date: 

`curl -H 'Content-Type: application/json' -XPUT 'localhost:9200/_template/**templatename**' -d '{"template": "portscans*", "mappings": {"scan": {"properties":{"timestamp": {"type" : "date", "format" : "epoch_second"} } } } }'`
