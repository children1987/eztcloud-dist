import App from './App'

// #ifndef VUE3
import Vue from 'vue'
Vue.config.productionTip = false
App.mpType = 'app'

import {http,BASE_URL} from '@/http/http.js';
import mqtt from './mqtt/mqtt.js'
Vue.prototype.$http = http;
Vue.prototype.BASE_URL = BASE_URL;
Vue.prototype.$util = {
  toUrl: (obj) => {
    let str = '?'
    let keys = Object.keys(obj)
    keys.forEach((key, index) => {
      if (obj[key] == null || obj[key] == undefined || obj[key]==="") {
        delete obj.key
        return
      }
      if (Object.prototype.toString.call(obj[key]) == '[object Array]') {
        obj[key].map(item => {
          str += `${key}=${item}&`
        })
      } else {
        str += `${key}=${obj[key]}&`
      }
    })
    return str.substring(0, str.length - 1)
  }
}
Vue.prototype.$mqtt = mqtt
const app = new Vue({
    ...App
})
app.$mount()
// #endif

// #ifdef VUE3
import { createSSRApp } from 'vue'
export function createApp() {
  const app = createSSRApp(App)
  return {
    app
  }
}
// #endif