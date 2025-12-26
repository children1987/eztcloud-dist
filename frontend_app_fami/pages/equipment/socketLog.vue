<template>
<view>
  <u-page-title>
    <view class="select">
      <u-goback />
    </view>
  </u-page-title>

  <u-page-content>
    <u-log id='log' :deviceLog="deviceLog" @toBottom="toBottom" @dateChange="dateChange"></u-log>
  </u-page-content>

</view>
</template>

<script>
export default {
  data() {
    return {
      deviceId:'',
      start_date:'',
      page:{
        page: 1,
        page_size: 15,
      },
      next: false,
      deviceLog:[
        // {
        //   title:'手动|张三',
        //   content:'开度0%',
        //   time:'2021/12/13 12:10:20',
        //   state:'1'
        // },
      ],
    }
  },
  onLoad(query) {
    this.deviceId = query.id;
    this.onSearch();
  },
  methods: {
    onSearch(init=true){
      uni.showLoading({
      	title: '加载中',
        mask:true
      });
      if(init){
        this.page.page = 1;
      }
      let data ={
        device:this.deviceId,
        start_date:"",
        page: this.page.page,
        page_size: this.page.page_size,
      }
      this.$http({
        url:`/api/operat_records/`,
        method:'get',
        data
      }).then(res=>{
        uni.hideLoading()
        if(res.statusCode == 200){
          console.log(res.data)
          if (init) {
              this.deviceLog = res.data.results.map(item=>{
                return{
                  title:item.creator?item.creator.nickname:' ',
                  content:item.description,
                  time:item.created_time,
                  state:item.result=='info'
                }
              });
          } else {
              if (res.data.results && res.data.results.length) {
                  let arr = res.data.results.map(item=>{
                    return{
                      title:item.creator?item.creator.nickname:' ',
                      content:item.description,
                      time:item.created_time,
                      state:item.result=='info'
                    }
                  });
                  this.deviceLog = this.deviceLog.concat(arr);
              }
          }
          if (res.data.next) {
              this.next = true;
          } else {
              this.next = false;
          }
        }
      }).catch(err=>{
        uni.hideLoading()
      })
    },
    toBottom(e){
      console.log(e)
      if (this.next) {
          this.page.page++;
          this.onSearch(false);
      }
    },
    dateChange(data){
      console.log(data)
      this.start_date = data;
      this.deviceLog = [];
      this.$nextTick(()=>{
        this.onSearch(true);
      })
    },
  }
}
</script>

<style lang="scss" scoped>

</style>
