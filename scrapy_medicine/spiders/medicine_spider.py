
from scrapy import Request
from scrapy.spiders import Spider
from scrapy_medicine.items import ScrapyMedicineItem

class MedicineSpider(Spider):
    name = 'medicine'   #spider name
    start_urls=['http://jbk.39.net/bw/yanke_t1/']  #spider将从该列表中开始抓取

    def parse(self, response):  #parse函数被当做一个生成器使用
        diseases = response.xpath('//div[@class="result_item"]')  #得到div class='result_item'的标签内容

        last_page = '/bw/yanke_t1_p33/'
        end_page_last_url='/bw/yanke_t1_p32/'

        for disease in diseases:
            disease_url = disease.xpath('.//p[@class="result_item_top_l"]/a/@href').extract()

            item = ScrapyMedicineItem()
            item['disease_name'] = disease.xpath('.//p[@class="result_item_top_l"]/a').attrib.get('title')
            if len(disease_url)!=0:
                yield Request(disease_url[0], callback=self.medicine_page,meta={'data':item})
        if len(response.xpath('//ul[@class="result_item_dots"]/li/span/a/@href').extract()):
            next_url = response.xpath('//ul[@class="result_item_dots"]/li/span/a/@href').extract()[-1]
        else:
            print("Cannot get information. Try again.")

        if last_page != next_url and end_page_last_url==next_url:
            judge_url=response.xpath('//ul[@class="result_item_dots"]/li/span/a/@href').extract()[-2]
            if judge_url==last_page:
                next_url = 'http://jbk.39.net' + next_url #获取下一页 url
                yield Request(next_url, callback=self.parse)    #重新请求下一页，并回调prase函数
        else:
            next_url = 'http://jbk.39.net' + next_url  # 获取下一页 url
            yield Request(next_url, callback=self.parse)  # 重新请求下一页，并回调prase函数

    def medicine_page(self,response):
        item = response.meta['data']
        more_medicine_urls = response.xpath('//p[@class="disease_title"]/a/@href').extract()
        for temp_url in more_medicine_urls:
            if temp_url[-5:]=='cyyp/':
                more_medicine_url=temp_url

                yield Request(more_medicine_url, callback=self.more_medicine_page,meta={'data':item})

    def more_medicine_page(self,response):
        item = response.meta['data']
        medicines = response.xpath('//li[@class="drug-list-btn clearfix"]/h4')
        for medicine in medicines:
            medicine_url = medicine.xpath('.//a/@href').extract()

            if len(medicine_url) != 0:
                yield Request(medicine_url[0], callback=self.xiangqing,meta={'data':item})

    def xiangqing(self, response):
        item = response.meta['data']
        print("正在爬取详情页面",response)
        item['medicine_name'] = response.xpath('//h1[@class="drug-layout-r-stor"]/text()').extract()

        divs=response.xpath('//ul[@class="drug-layout-r-ul"]')
        body=['','','','','','','','','','','','']

        for i in range(0,len(divs.xpath('.//i/text()').extract())):
            body[i] += divs.xpath('.//i/text()').extract()[i].strip()

        p = "".join(divs.xpath('.//div/p').extract())
        cleanp=''
        skip=0
        for i in range (0,len(p)-1):
            if (p[i]=='<'and p[i+1]=='a')or (p[i]=='['and p[i+1]=='详') or (p[i]=='<'and p[i+1]=='/' and p[i+2]=='a'):
                skip=1
            elif p[i-1]=='>'or p[i-1]==']' :
                skip=0
            if(skip==0):
               cleanp+=p[i]

        pList=['','','','','','','','','','']
        num =-1
        paste=0
        for i in range(0,len(cleanp)-1):
            if cleanp[i]=='>'and cleanp[i+1]!='<':
                paste=1
                num+=1
            elif cleanp[i]=='<':
                paste=0

            if paste==1:
                pList[num]+=cleanp[i]

        for i in range(0,min(num+1,len(divs.xpath('.//i/text()').extract()))):
            pList[i]=pList[i].replace(' ','')
            pList[i]=pList[i].replace('\r','')
            pList[i]=pList[i].replace('\n', '')
            pList[i]=pList[i].replace('>', '')
            pList[i]=pList[i].replace('\u3000','')
            pList[i] = pList[i].replace('', '')

            if body[i][0]=='适':
                item['indication'] = pList[i]

            elif body[i][0]=='主':
                item['components'] = pList[i]

            elif body[i][0]=='功':
                item['functions'] =  pList[i]

        use = "".join(divs.xpath('.//div/text()').extract())
        use = use.replace(' ', '')
        use = use.replace('\r', '')
        use = use.replace('\n', '')
        use = use.replace('>', '')
        use = use.replace('\u3000', '')
        item['usage'] = use

        print("爬取完成")
        yield item