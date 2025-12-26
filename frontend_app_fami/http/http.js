export const BASE_URL = "https://api.isw.hotanzn.com"; //接口地址
// export const BASE_URL = "http://192.168.1.11:8000"; //接口地址
let ajaxTimes=0;
export const http = (options) => {
  // console.log(options.url)
  // console.log(BASE_URL + options.url)
  let token = uni.getStorageSync('token')||''
  let header={};
  if(token){
    header.Authorization = `JWT ${token}`;
  }
  ajaxTimes++;
  uni.showLoading({
		  title: "加载中",
	    mask: true,
	});
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || "GET",
      data: options.data || {},
      // Authorization
      header,
      success: (res) => {
        if (res == "") {
          return uni.showToast({
            icon: "loading",
            title: "获取数据失败",
          });
        }
        if (res.statusCode == 401) {
          uni.navigateTo({
            url: `/pages/login/login`
          })
        }
        resolve(res);
      },
      fail: (err) => {
        return uni.showToast({
          icon: "loading",
          title: "请求失败",
        });
        reject(err);
      },
      // 完成之后关闭加载效果
			complete:()=>{
				ajaxTimes--;
				if(ajaxTimes===0){
			        //  关闭正在等待的图标
			        uni.hideLoading();
			    }
			}
    });
  });
};
