import mqtt from "./mqtt.min.js";

let basemqtt = 'wxs://broker.isw.hotanzn.com';

function getUUID(len, radix) {
  let chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split('');
  let uuid = [], i;
  radix = radix || chars.length;
  if (len) {
    for (i = 0; i < len; i++) uuid[i] = chars[0 | Math.random() * radix];
  } else {
    let r;
    uuid[8] = uuid[13] = uuid[18] = uuid[23] = '-';
    uuid[14] = '4';
    for (i = 0; i < 36; i++) {
      if (!uuid[i]) {
        r = 0 | Math.random() * 16;
        uuid[i] = chars[(i == 19) ? (r & 0x3) | 0x8 : r];
      }
    }
  }
  return uuid.join('');
}
function returnMqttClient(){ 
  const options = {
    connectTimeout: 2000,
    clientId: getUUID(32, 16),
    username: 'frontend',
    password: 'df3efi30Fdf8eizSSFEfz9zfz9',
    clean: true,
    port: 7886,
    useSSL: true, 
    path:'/mqtt'
  }
  return mqtt.connect(basemqtt, options)
}

function mqttClient(){
  this.client = returnMqttClient()
}
mqttClient.prototype.connect = function(topic_list,callback){
  // mqtt连接cb
  this.client.on('connect', function () {
    console.log("连接成功")
    //订阅主题 
    this.subscribe(topic_list, function (err) {
      if (!err) {
        console.log("订阅成功!")
      }else{
        console.log(err)
      }
    });
    // 接收消息处理
    this.on('message', (topic, message) => {
      try {
        callback(topic, message.toString())
      } catch (err) {
        console.log(err)
      }
    });
  });
  this.client.on('error',err=>{
    console.log('err',err)
  })
}
mqttClient.prototype.unsubscribe = function(topic){
  if (topic) {
    this.client.unsubscribe(topic)
  } else {
    this.client.end()
  }
}
mqttClient.prototype.publish = function(topic,msg){
  if(typeof msg != 'string')throw Error('mqttMessag should be string');
  this.client.publish(topic,msg)
}
export default {
  mqttClient
}