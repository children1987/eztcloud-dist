docker run --network=host -d --name isw_v2_emqx5.8.0 --restart unless-stopped \
    -v /workspace/isw_v2/mqtt_broker/emqx/persist/data:/opt/emqx/data \
    -v /workspace/isw_v2/mqtt_broker/emqx/persist/log:/opt/emqx/log \
    -v /workspace/isw_v2/mqtt_broker/emqx/emqx_test.conf:/opt/emqx/etc/emqx.conf \
    -v /workspace/isw_v2/mqtt_broker/emqx/acl.conf:/opt/emqx/etc/acl.conf \
    -v /workspace/ssl/eztcloud.com:/eztcloud.com \
    emqx/emqx:5.8.0
