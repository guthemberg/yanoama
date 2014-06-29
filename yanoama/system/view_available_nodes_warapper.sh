NODES_FILE=~/yanoama/nodes.pck
if [ -e ]; then
  python ~/yanoama/yanoama/monitoring/show_rtt_nodes.py $NODES_FILE |sort -t, -k1 -nr
else
  echo "$NODES_FILE does not exist"
fi
