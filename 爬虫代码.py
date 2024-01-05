import urllib.request
from bs4 import BeautifulSoup
import re
import xlwt



# 影片详情链接的规则
findLink = re.compile(r'<a href="(.*?)">')    # 创建正则表达式对象，表示规则
# 影片图片的链接
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)    # re.S忽略换行符
# 影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
# 概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
# 找到影片相关内容
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)



def getData(baseurl):
    datalist = []
    for i in range(0, 10):   # 调用获取页面信息的函数
        url = baseurl+str(i * 25)
        html = askURL(url)    # 一个页面的html
        soup = BeautifulSoup(html, 'html.parser')  # 把返回的html源代码，进行解析。
        for item in soup.findAll('div', class_='item'):

            data = []    # 保存每一个电影的信息
            item = str(item)  # 转换成字符串对象

            link = re.findall(findLink,item)[0]  # 获取影片详情的超链接
            data.append(link)

            imgSrc = re.findall(findImgSrc, item)[0]      # 获取图片链接
            data.append(imgSrc)

            titles = re.findall(findTitle, item)     # 添加片名，片名可能有一个，也可能有两个
            if len(titles)==2:
                ctitle = titles[0]          # 中文名
                data.append(ctitle)
                otitle = titles[1].replace("/", "")   # 英文名中有无关的符号，去除
                data.append(otitle)         # 英文名
            else:
                data.append(titles[0])
                data.append(' ')    # 留空 ，因为要放到数据库

            rating = re.findall(findRating, item)[0]
            data.append(rating)                         # 评分

            judgeNum = re.findall(findJudge,item)[0]
            data.append(judgeNum)                   # 添加评价人数

            inq = re.findall(findInq,item)
            if len(inq) != 0:
                inq=inq[0].replace("。", "")
                data.append(inq)                        # 添加概述
            else:
                data.append("无概述")

            bd = re.findall(findBd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?', ' ', bd)  # 去掉<br/>
            bd = re.sub('/',' ',bd)    # 去掉/
            data.append(bd.strip())    # 去掉前后空格

            datalist.append(data)    # 将一个电影的信息放到datalist
    return datalist

def askURL(url):
    """
    该函数，通过参数传进来的url对该url发起一个请求，并获取服务器返回的响应response，最后把获取的响应的html数据return，返回出去。
    """
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    request = urllib.request.Request(url,headers=head)
    html = ""
    try:
        response=urllib.request.urlopen(request)
        html=response.read().decode('utf-8')
    except urllib.error.URLError as e:
        if hasattr(e,'code'):
            print(e.code)
        if hasattr(e,'reason'):
            print(e.reason)
    return html

# 保存信息
def saveDate(datalist, savepath):
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)        # 创建Workbook对象
    sheet = book.add_sheet('豆瓣电影Top250', cell_overwrite_ok=True)   # 创建工作表
    col = ('电影详情链接', '图片链接', '影片中文片名', '影片外国名', '评分', '评价数', '概况', '相关信息')
    for i in range(0,8):
        sheet.write(0, i, col[i])   # 列名
    for i in range(0,250):
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1, j, data[j])    # 写入数据
    book.save(savepath)       # 保存

# 程序入口
if __name__ == '__main__':
    baseurl = "https://movie.douban.com/top250?start="  # 定义爬取的网页
    datalist = getData(baseurl)  # 获取数据
    savepath = "原始数据.xls"  # 定义保存路径
    saveDate(datalist, savepath)  # 保存数据
    print('爬取完成!')
