HOME=~
YANOAMA_HOME=${HOME}/yanoama

if [ `pgrep -f pilotd|wc -l` -eq 0 ]; then
    sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd start
fi