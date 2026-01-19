# ESAUpdate

已合并到 [NAT1 Traversal](https://github.com/Guation/nat1_traversal)

## 使用方法
1. 在[ESA](https://esa.console.aliyun.com/siteManage/list)控制台点击新增站点，绑定您的域名，其值与`config.json`的`domain`，我们假设您绑定的域为`example.com`

2. 绑定完成后点击您的站点，进入站点站点概况。

3. 点击DNS->记录->添加记录，主机记录与`config.json`的`sub_domain`字段相同，我们假设主机记录为`www`，记录值随意填写。

4. 点击规则->回源规则->新增规则，规则名称与`config.json`的`sub_domain`字段相同。规则内容->`自定义规则`->`主机名``等于``www.example.com`，则执行->`回源协议和端口`->`配置`->回源协议根据实际需求填写，端口保持默认。

5. 打开[RAM 访问控制](https://ram.console.aliyun.com/users)

6. 新建用户->快速创建->访问方式:编程访问,用户权限:QcloudTEOFullAccess->创建用户

7. 创建用户->登录名称随意->使用永久 AccessKey 访问->我确认必须创建 AccessKey->确定->勾选用户->新增授权->权限策略:AliyunESAFullAccess->确认新增授权

8. 使用`AccessKey ID`作为`id`，使用`AccessKey Secret`作为`token`填入`config.json`

9. 运行`esa_update.pyz`

10. 在[NAT1 Traversal](https://github.com/Guation/nat1_traversal)的`config.json`中将`type`字段设置为`web`，`dns`字段设置为`webhook`，`id`字段设置为`http//:127.0.0.1:8080/`

11. 运行`nat1_traversal.tgz`

12. 由于`esa_update`与`nat1_traversal`均使用`config.json`作为默认配置文件，请勿将他们放到一个文件夹，如果一定要放到同一个文件夹请使用`-c`指定配置文件。

13. 先运行`esa_update`后运行`nat1_traversal`
