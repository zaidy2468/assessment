import scrapy
from ..items import ThegazetteItem


class ScraperSpider(scrapy.Spider):
    name = "scraper"
    allowed_domains = ["thegazette.co.uk"]
    start_urls = ["https://www.thegazette.co.uk/all-notices/notice?text=&categorycode-all=all&noticetypes=&location-postcode-1=&location-distance-1=1&location-local-authority-1=&numberOfLocationSearches=1&start-publish-date=&end-publish-date=&edition=&london-issue=&edinburgh-issue=&belfast-issue=&sort-by=&results-page-size=10"]

    def __init__(self, *args, **kwargs):
        super(ScraperSpider, self).__init__(*args, **kwargs)
        #setting increment counter for pagination
        self.recursion_counter = 0
    def parse(self, response):


        #selecting the main div which contains all hyperlinks for notices on single page

        div_selector=response.css('div.content')
        articles_with_id = div_selector.xpath('.//article[@id]')
        #iterating through every notice card component
        for article_selector in articles_with_id:
            full_page_url=article_selector.css('div a::attr(href)').get()
            article_id = full_page_url.split('/')[-1]
            xpath_selector = f'//*[@id="item-{article_id}"]/div/header/h3[@class="title"]/a/text()'
            name=article_selector.xpath(xpath_selector).get()
            print(name)

            yield scrapy.Request(response.urljoin(full_page_url),callback=self.full_page,meta={'name': name})

        # pagination
        next_page=response.xpath('//*[@id="search-results"]/nav/div/ul/li[13]/ul/li[2]/a/@href').get()
        if next_page and self.recursion_counter < 15:
            self.recursion_counter += 1
            yield scrapy.Request(next_page,callback=self.parse)

    def full_page(self,response):

        #scraping from full page


        notice_category=response.css('dd.category::text').get()
        notice_type=response.css('dd.notice-type::text').get()
        publication_date= response.css('dd[property="gaz:hasPublicationDate"] time::text').get()
        if not publication_date:
            publication_date = response.css('dd[property="gaz:hasPublicationDate"]::text').get()
        notice_deadline=response.css('dd[property="personal-legal:hasClaimDeadline"]::text').get()
        edition_dt = response.xpath('//dt[text()="Edition:"]')

        if edition_dt:
            # Get the next sibling dd element
            edition_dd = edition_dt.xpath('following-sibling::dd[1]')

            if edition_dd:
                # Extract the text content of the dd element
                edition = edition_dd.xpath('string()').get().strip()


        notice_id = response.css('dd[property="gaz:hasNoticeID"]::text').get()
        notice_code=response.css('dd[property="gaz:hasNoticeCode"]::text').get()
        processed_notice_timeline=response.xpath('//*[@id="main_content"]/div/div[1]/div[2]/aside//text()').getall()
        notice_timeline_cleaned=[item for item in processed_notice_timeline if item.strip()]
        notice_timeline=[item.replace('\n', '').replace('  ', ' ').replace('   ', ' ') for item in notice_timeline_cleaned]
        processed_notice_specifics=response.xpath('//*[@id="main_content"]/div/div[1]/div[2]/article//text()').getall()
        cleaned_notice_specifics=[item for item in processed_notice_specifics if item.strip()]
        notice_specifics = [item.replace('\n', '').replace('  ', ' ').replace('   ', ' ') for item in cleaned_notice_specifics]



        #invoking item pieline for scraped data to process further
        item = ThegazetteItem()
        item['name']=response.meta.get('name')
        item['edition'] = edition
        item['notice_category'] =notice_category
        item['notice_type'] =notice_type
        item['publication_date'] =publication_date
        item['notice_deadline'] =notice_deadline
        item['notice_id'] =notice_id
        item['notice_code'] =notice_code
        item['notice_specifics'] =notice_specifics
        item['notice_timeline'] =notice_timeline
        yield item
