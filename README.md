# 注意事项
此代码是把输入的表格转换成详细的纯文本描述。
## 部署
注意配置大模型所对应的环境变量和端口

需要在config.py中配置大模型参数，这里列举了两个大模型参数，如果还有更多可以在后面追加。

![image-20240707152452016](imgs/1.png)


端口配置：
![image-20240707152632048](imgs/2.png)

## 路由

```
/api/table2text  #接收json
/api/table2text_excel #接收excel文件
/api/table2text_json_file #接收json文件
```