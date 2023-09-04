import requests
import urllib.request as request
import json

# Get请求用来获取数据，Post 请求用来提交数据

# r = requests.get('http://httpbin.org/get')
# print(r.text)
url_head = "http://10.0.7.208:26666/user/secUid/"
sec_id = 'MS4wLjABAAAAFeT0BJ7CRPN024oIb-TlsOMTlu3uVMYg6Sw7mYHwDjA'
# anchors_html = request.urlopen(url_head+sec_id).read()
# anchors_info = json.loads(anchors_html)
# print(anchors_info)

# response = requests.get(url_head+sec_id)
# print(f"当前请求的响应状态码为：{response.status_code}")  # status_code为响应状态码，值为200时表明成功，其他的都是有问题
# print(response.text)
# print(response.json())

url = 'https://www.baidu.com/s?wd=python'
# headers的作用是伪装成浏览器对网址进行访问，否则的话容易被拒绝
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
# response = requests.get(url, headers=headers)
# print(f"当前请求的响应状态码为：{response.status_code}")
'''
使用response.content时，返回的是服务器响应数据的原始二进制字节流，response.content的类型是bytes，通常用来保存图片等二进制文件。
response.content 可以返回任何网页的数据，没有对响应数据解码，所以我们可以用deocde()来设置编码方式，这样可以得到正确的编码结果。
'''
# print(response.content.decode())

'''
使用response.text时，Requests会基于HTTP响应的文本编码自动解码响应内容，response.text的类型是str，大多数Unicode字符集都能被无缝地解码。
response.text是根据HTTP头部对响应的编码作出有根据的推测，推测出文本编码方式，然后进行解码。注意，这里是推测，所以response.text不能正确解码所有的网页数据，如百度首页。
当不能使用response.text时，使用response.content.deocde()。
'''
# print(response.text)

# 打印请求头信息
# print(response.request.headers)

wd = '张三同学'
pn = 1
# response = requests.get('https://www.baidu.com/s', params={'wd': wd, 'pn': pn}, headers=headers)
# print(response.url)  # https://www.baidu.com/s?wd=%E5%BC%A0%E4%B8%89%E5%90%8C%E5%AD%A6&pn=1 可以看到已经被自动编译


url = 'https://fanyi.baidu.com/sug'
# 请求参数
date = {
    'kw':'python'
}
# 发送请求返回响应对象
response = requests.post(url,data=date,headers=headers)
print(response.json())
print(response.status_code)