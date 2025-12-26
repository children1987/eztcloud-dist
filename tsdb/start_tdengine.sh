docker run -d --name isw_v2_tdengine \
  -v /data/taos/dnode/data:/var/lib/taos \
  -v /data/taos/dnode/log:/var/log/taos \
  --network=host \
  --restart unless-stopped \
  tdengine/tdengine:3.3.5.0
