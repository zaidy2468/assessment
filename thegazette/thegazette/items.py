# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ThegazetteItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    notice_category=scrapy.Field()
    notice_type=scrapy.Field()
    publication_date=scrapy.Field()
    notice_deadline=scrapy.Field()
    edition=scrapy.Field()
    notice_id=scrapy.Field()
    notice_code=scrapy.Field()
    notice_specifics=scrapy.Field()
    notice_timeline=scrapy.Field()
    pass
