#!/usr/bin/env bash

### Edit these variables
IP_OR_HOSTNAME='0.0.0.0'


if [ -f /etc/debian_version ]
then
	DEBIAN='True'
elif [ -f /etc/redhat-release ]
then
	RHEL='True'
fi


if [[ "$DEBIAN" == 'True' ]]
then	
	sudo apt-get update
	sudo apt-get install openjdk-8-jdk-headless -y

	wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
	echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-6.x.list
	
	sudo apt-get update
	sudo apt-get install python3 python3-pip git gcc make clang libpcap-dev kibana elasticsearch -y

fi

if [[ "$RHEL" == 'True' ]]
then
	sudo yum -y install java-1.8.0-openjdk

	sudo rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch
	sudo curl 'https://raw.githubusercontent.com/heywoodlh/Port-Crawler-Py/master/rhel-repo/elastic.repo' -o '/etc/yum.repos.d/elastic.repo'
	sudo yum -y install kibana elasticsearch

	sudo yum -y install epel-release
	sudo yum -y install python36
	sudo ln -s /usr/bin/python3.6 /usr/bin/python3
	curl https://bootstrap.pypa.io/get-pip.py -o ~/get-pip.py 
	sudo /usr/bin/python3.6 ~/get-pip.py
	rm ~/get-pip.py

	sudo yum -y install git gcc gcc-c++ kernel-devel clang libpcap-devel
fi

### Don't edit below unless you know what you are doing

PWD="$(pwd)"
sudo mkdir -p /opt/
sudo chown -R "$USER:$USER" /opt
git clone https://github.com/heywoodlh/Port-Crawler-Py /opt/Port-Crawler-Py


sudo sed -i 's/#cluster.name: my-application/cluster.name: port-crawler/g' /etc/elasticsearch/elasticsearch.yml
sudo sed -i 's/#network.host: 192.168.0.1/network.host: 127.0.0.1/g' /etc/elasticsearch/elasticsearch.yml
sudo systemctl enable elasticsearch.service
sudo systemctl start elasticsearch.service



sudo sed -i 's/#server.port: 5601/server.port: 5601/g' /etc/kibana/kibana.yml
sudo sed -i 's/#server.host: "localhost"/server.host: '"$IP_OR_HOSTNAME"'/g' /etc/kibana/kibana.yml
sudo systemctl enable kibana.service
sudo systemctl restart kibana.service




sudo chown -R "$USER:$USER" /opt
cd /opt
git clone https://github.com/robertdavidgraham/masscan
cd masscan
make
sudo cp bin/masscan /usr/bin/



sudo chown -R "$USER":"$USER" /opt/Port-Crawler-Py
sudo pip3 install -r /opt/Port-Crawler-Py/requirements.txt


### Set default mapping for portscans to date

ERR=1
MAX_TRIES=4 
COUNT=0

echo 'Please wait while attempting to connect to Elasticsearch...'
while [  "$COUNT" -lt "$MAX_TRIES" ]
do
	curl -H 'Content-Type: application/json' -XPUT 'localhost:9200/_template/**templatename**' -d '{"template": "portscans*", "mappings": {"scan": {"properties":{"timestamp": {"type" : "date", "format" : "epoch_second"} } } } }'
	sleep 10
	if [ "$?" -eq 0 ]
	then
		cd "$PWD"
		exit 0
	fi
	COUNT=$(("${COUNT}"+1))
done
echo "Unable to connect to Elasticsearch"
exit "$ERR"
