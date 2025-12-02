<template>
    <view>
        <!--标题和返回-->
		<cu-custom :bgColor="NavBarColor" isBack :backRouterName="backRouteName">
			<block slot="backText">返回</block>
			<block slot="content">软著文件记录</block>
		</cu-custom>
		 <!--表单区域-->
		<view>
			<form>
              <my-date label="更新时间：" v-model="model.updateTime" placeholder="请输入更新时间"></my-date>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">对话ID：</text></view>
                  <input  placeholder="请输入对话ID" v-model="model.sessionId"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">文件类型：</text></view>
                  <input  placeholder="请输入文件类型" v-model="model.fileType"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">文件分类：</text></view>
                  <input  placeholder="请输入文件分类" v-model="model.fileCategory"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">文件名：</text></view>
                  <input  placeholder="请输入文件名" v-model="model.filename"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">文件路径：</text></view>
                  <input  placeholder="请输入文件路径" v-model="model.filePath"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">文件大小(字节)：</text></view>
                  <input type="number" placeholder="请输入文件大小(字节)" v-model="model.fileSize"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">MIME类型：</text></view>
                  <input  placeholder="请输入MIME类型" v-model="model.mimeType"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">文件扩展名：</text></view>
                  <input  placeholder="请输入文件扩展名" v-model="model.fileExtension"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">质量状态：</text></view>
                  <input  placeholder="请输入质量状态" v-model="model.qualityStatus"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">质量得分(0-100)：</text></view>
                  <input type="number" placeholder="请输入质量得分(0-100)" v-model="model.qualityScore"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">质检报告JSON：</text></view>
                  <input  placeholder="请输入质检报告JSON" v-model="model.qualityReportJson"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">代码行数(仅代码文件)：</text></view>
                  <input type="number" placeholder="请输入代码行数(仅代码文件)" v-model="model.codeLines"/>
                </view>
              </view>
              <view class="cu-form-group">
                <view class="flex align-center">
                  <view class="title"><text space="ensp">文档字数：</text></view>
                  <input type="number" placeholder="请输入文档字数" v-model="model.docWordCount"/>
                </view>
              </view>
				<view class="padding">
					<button class="cu-btn block bg-blue margin-tb-sm lg" @click="onSubmit">
						<text v-if="loading" class="cuIcon-loading2 cuIconfont-spin"></text>提交
					</button>
				</view>
			</form>
		</view>
    </view>
</template>

<script>
    import myDate from '@/components/my-componets/my-date.vue'

    export default {
        name: "CopyrightFileForm",
        components:{ myDate },
        props:{
          formData:{
              type:Object,
              default:()=>{},
              required:false
          }
        },
        data(){
            return {
				CustomBar: this.CustomBar,
				NavBarColor: this.NavBarColor,
				loading:false,
                model: {},
                backRouteName:'index',
                url: {
                  queryById: "/apply/copyrightFile/queryById",
                  add: "/apply/copyrightFile/add",
                  edit: "/apply/copyrightFile/edit",
                },
            }
        },
        created(){
             this.initFormData();
        },
        methods:{
           initFormData(){
               if(this.formData){
                    let dataId = this.formData.dataId;
                    this.$http.get(this.url.queryById,{params:{id:dataId}}).then((res)=>{
                        if(res.data.success){
                            console.log("表单数据",res);
                            this.model = res.data.result;
                        }
                    })
                }
            },
            onSubmit() {
                let myForm = {...this.model};
                this.loading = true;
                let url = myForm.id?this.url.edit:this.url.add;
				this.$http.post(url,myForm).then(res=>{
				   console.log("res",res)
				   this.loading = false
				   this.$Router.push({name:this.backRouteName})
				}).catch(()=>{
					this.loading = false
				});
            }
        }
    }
</script>
