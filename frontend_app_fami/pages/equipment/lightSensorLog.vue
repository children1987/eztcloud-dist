<template>
<view>
  <u-page-title>
    <view class="select">
      <u-goback />
    </view>
  </u-page-title>

  <u-page-content>
    <u-log :deviceLog="deviceLog" @toBottom="toBottom" @dateChange="dateChange"></u-log>
  </u-page-content>

</view>
</template>

<script>
export default {
  data() {
    return {
      deviceId:'',
      deviceLog:[
        {
          title:'手动|张三',
          content:'电压380V|电流380A',
          time:'2021/12/13 12:10:20',
          state:'1'
        },
        {
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/14 15:10:20',
          state:'1'
        },
        {
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/15 18:10:20',
          state:'1'
        },
        {
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/15 18:10:20',
          state:'1'
        },
        {
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/15 18:10:20',
          state:'1'
        },
        {
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/15 18:10:20',
          state:'1'
        },
        {
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/15 18:10:20',
          state:'1'
        },
        {
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/15 18:10:20',
          state:'1'
        },
        {
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/15 18:10:20',
          state:'1'
        },
        {
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/15 18:10:20',
          state:'1'
        },
       
        
      ],
    }
  },
  onLoad(query) {
    this.deviceId = query.id;
  },
  methods: {
    toBottom(e){
      console.log(e)
      this.deviceLog = this.deviceLog.concat([{
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/15 18:10:20',
          state:'1'
        },
        {
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/15 18:10:20',
          state:'1'
        },
        {
          title:'自动',
          content:'电压380V|电流380A',
          time:'2021/12/15 18:10:20',
          state:'1'
        },])
    },
    dateChange(data){
      console.log(data)
    },
  }
}
</script>

<style lang="scss" scoped>
.select {
  width: 200rpx;
}

::v-deep .uni-select {
  border: none !important;
}
</style>
