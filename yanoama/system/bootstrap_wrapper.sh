echo -n "sleeping awhile... "
sleep 30 && echo "running bootstrap." && sh /tmp/bootstrap.sh >> /tmp/last_bootstrap.log &
