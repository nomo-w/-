## 接口文档
>维护人员：**nomo**
>创建时间：2020-07-06

>>> + 发送验证码


### 基础路径
> base URL：http://111.111.111.111:8888
### 请求头
>**Content-Type: application/json**
### 签名方法
> 对所有请求参数 如：to=123,yzm=111 按照参数名和参数值构造成字符串，格式为：to+123+yzm+111+key+密钥. 根据上面的示例得到的构造结果为：to123yzm111keyIYEAouewMcyUYEk35V8rHik9LkQU0C. 把拼装好的字符串采用 utf-8 编码，使用 MD5 算法对字符串进行签名，计算得到 signature 参数值，
### 密钥
> IYEAouewMcyUYEk35V8rHik9LkQU0C


#### 接口说明 **发送验证码**
- **API接口**
>**/api/send**
- **请求方法**
>**POST**

- **请求参数**
> 
| 请求参数      |     参数类型 |   参数说明   |
| :-------- | :--------| :------ |
| to|  str|  手机号|
| yzm|   str|  验证码|
| signature|  str|  签名|


- **返回参数**
> 
| 返回参数      |     参数类型 |   参数说明   |
| :-------- | :--------| :------ |
| data    |   str |  ok或者失败原因|
| status      |   int |  200(成功)/500(失败)|

- **返回成功示例**
>    
```python 
{
    "data": "ok",
    "status": 200
}
```
