# language: zh-CN
功能: JeecgBoot基础系统API测试
  作为一个JeecgBoot系统用户
  我希望能够访问基础的系统API
  以便验证系统的基本功能正常

  背景:
    假如JeecgBoot系统已启动并运行正常

  场景: 获取系统基础信息
    当我访问系统信息接口"/jeecg-boot/sys/randomImage"
    那么系统应该返回成功状态码200
    并且响应时间应该少于3秒

  场景: 验证系统健康检查
    当我访问健康检查接口"/jeecg-boot/actuator/health"  
    那么系统应该返回成功状态码200
    并且响应体应该包含"UP"状态

  场景: 测试系统基础配置
    当我访问系统配置接口"/jeecg-boot/sys/common/static"
    那么系统应该返回成功状态码200
    并且响应应该是有效的JSON格式

  场景: 验证API文档可访问性
    当我访问API文档接口"/jeecg-boot/doc.html"
    那么系统应该返回成功状态码200
    并且响应头应该包含"text/html"类型

  场景大纲: 系统接口响应时间验证
    当我访问接口"<接口路径>"
    那么响应时间应该少于<最大响应时间>秒

    例子:
      | 接口路径                           | 最大响应时间 |
      | /jeecg-boot/sys/randomImage        | 3           |
      | /jeecg-boot/actuator/health        | 2           |
      | /jeecg-boot/sys/common/static      | 5           |