#!/usr/bin/env bash

### Edit these variables
IP_OR_HOSTNAME='0.0.0.0'



### Don't edit below unless you know what you are doing

PWD="$(pwd)"
sudo mkdir -p /opt/
sudo chown -R "$USER:$USER" /opt
git clone https://github.com/heywoodlh/Port-Crawler-Py /opt/Port-Crawler-Py
cd Port-Crawler-Py



### Install Java

sudo apt-get update
sudo apt-get install openjdk-8-jdk -y


### Elastic repository install

wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" > /etc/apt/sources.list.d/elastic-6.x.list

### Elasticsearch install

sudo apt-get update
sudo apt-get install elasticsearch -y
sudo sed -i 's/#cluster.name: my-application/cluster.name: port-crawler/g' /etc/elasticsearch/elasticsearch.yml
sudo sed -i 's/#network.host: 192.168.0.1/network.host: 127.0.0.1/g' /etc/elasticsearch/elasticsearch.yml
sudo systemctl enable elasticsearch.service
sudo systemctl start elasticsearch.service


### Kibana install

sudo apt-get install kibana -y
sudo sed -i 's/#server.port: 5601/server.port: 5601/g' /etc/kibana/kibana.yml
sudo sed -i 's/#server.host: "localhost"/server.host: '"$IP_OR_HOSTNAME"'/g' /etc/kibana/kibana.yml
sudo systemctl enable kibana.service
sudo systemctl restart kibana.service



### Masscan install

sudo apt-get install git gcc make clang libpcap-dev -y
sudo chown -R "$USER:$USER" /opt
cd /opt
git clone https://github.com/robertdavidgraham/masscan
cd masscan
make
sudo cp bin/masscan /usr/bin/


### Install Python3

sudo apt-get install python3 python3-pip -y
sudo chown -R "$USER":"$USER" /opt/Port-Crawler-Py
sudo pip3 install -r /opt/Port-Crawler-Py/requirements.txt


### Set default mapping for portscans to date
curl -H 'Content-Type: application/json' -XPUT 'localhost:9200/_template/**templatename**' -d '{"template": "portscans*", "mappings": {"scan": {"properties":{"timestamp": {"type" : "date", "format" : "epoch_second"} } } } }'

cd "$PWD"
