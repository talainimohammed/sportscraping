import scrapy
from pymongo import MongoClient
from scrapy import Item, Field



class ArticleItem(Item):
    title = Field()
    category = Field()
    link = Field()
    article = Field()

class SportSpider(scrapy.Spider):
    name = "sport"
    allowed_domains = ["www.rtl.be"]
    start_urls = ["https://www.rtl.be/sport"]

    def __init__(self):
        self.client = MongoClient("mongodb+srv://talainimohammed:399nlM1nmTtwP5Ea@cluster0.qj37baa.mongodb.net/")
        self.db = self.client.scrapingdb

    def inserttoDb(self,title, category, link, article):
        doc={"title":title, "category":category, "link":link, "article":article}
        inserted=self.db.sport.insert_one(doc)
        return inserted.inserted_id
    
    def parse_article(self, response, item):
        for sub_heading in response.css('r-article--section'):
            item['article'] = sub_heading.css('p::text').get()
            insertedrow=self.inserttoDb(item['title'], item['category'], item['link'], item['article'])
            #yield item

    def parse(self, response):
        for sub_heading in response.css('r-viewmode'):
            myquery = { "title": sub_heading.css('h3.r-article--title a::text').get()} 
            if self.db.sport.count_documents(myquery) > 0:
                print('Article already exists')
                continue
            else:
                item = ArticleItem()
                item['title'] = sub_heading.css('h3.r-article--title a::text').get()
                item['category'] = sub_heading.css('a::attr(href)').get().split('/')[2]
                item['link'] = sub_heading.css('a::attr(href)').get()
                yield response.follow(item['link'], self.parse_article, cb_kwargs=dict(item=item))

    def close(self, reason):
        self.client.close()