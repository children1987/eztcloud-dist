docker run -d \
  --name isw_v2_influxdb \
  --restart unless-stopped \
  --network host \
  -e DOCKER_INFLUXDB_INIT_MODE=setup \
  -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
  -e DOCKER_INFLUXDB_INIT_PASSWORD=${DOCKER_INFLUXDB_INIT_PASSWORD} \
  -e DOCKER_INFLUXDB_INIT_ORG=shhk \
  -e DOCKER_INFLUXDB_INIT_BUCKET=isw2-bucket \
  -e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN} \
  -e DOCKER_INFLUXD_SESSION_LENGTH=1 \
  -v /workspace/isw_v2/influxdb/data:/var/lib/influxdb2 \
  -v /workspace/isw_v2/influxdb/config:/etc/influxdb2 \
  influxdb:2.7-alpine
