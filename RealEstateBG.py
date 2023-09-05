from scrapy import Selector
import requests
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# create the class
class RealEstate:
    def __init__(self, url, no_rooms):
        self.url = url  # url to be scraped
        self.no_rooms = no_rooms  # number of rooms parameter to be used for further analysis
# function to scrape and add the data to a dataframe
    def analyze(self):
        get_page_numbers = requests.get(self.url)  # read the webpage
        get_page_numbers.encoding = get_page_numbers.apparent_encoding  # encoding
        page_nums_txt = get_page_numbers.text  # response to text
        page_nums = re.findall(r'(Страница\s\d+\sот\s\d+)', page_nums_txt)  # regex to look for the string with number of pages
        pages = int(page_nums[0][-2:])
        print(pages)
        
        price_pattern = r'(\d+\s\d+\sEUR)|(Цена при запитване)'  # either 000 000 eur or "Цена при запитване"
        area_pattern = r'(\d+\sкв.м)'  #looking for "кв.м" in the text
        prices_all = []
        area_all = []
        prices_all_new = []
        xpath = '//td[contains(text(), "кв.м")]'  # xpath for "кв.м" in the text
        xpath_prices = '//div[contains(@class, "price")]'  # xpath for price
        area_modified = []
        prices_final = []
        
        # iterate over the page numbers with offers
        for i in range(1,pages + 1):
            imoti = requests.get(str(self.url[:-1] + '{}').format(i))
            imoti.encoding = imoti.apparent_encoding
            txt = imoti.text
            sel = Selector(imoti)
            prices = re.findall(price_pattern, txt)
            
            for j in range(len(prices)):
                prices_all.append(prices[j])
    
            offer_prices = sel.xpath(xpath_prices).extract()
            offer_text = sel.xpath(xpath).extract()  # всички текстове от обявите
            print(len(offer_prices))
            # print(offer_text)
        
            for m in range(len(offer_text)):
                kv_m = re.findall(area_pattern, offer_text[m])
                area_all.append(kv_m)
                price_new = re.findall(price_pattern, offer_prices[m])
                prices_all_new.append(price_new)
                # print(area_modified[m][0])  # избирам само 1ви елемент от всеки елемент в списъка 
        print(len(area_all))
        print(len(prices_all_new))
        
        
        for i in range(len(area_all)):
            area_modified.append(int(area_all[i][0][:3].strip()))
            
        for i in range(len(prices_all_new)):
            prices_final.append(prices_all_new[i])
            
        # use the two lists to create a dataframe
        df = pd.DataFrame(data=[area_modified, prices_final]).T
        df.columns = ['m2', 'EUR']
        # data cleaning
        df['EUR'] = df['EUR'].astype('str')
        df['EUR'] = df['EUR'].str.replace("[(\'","")
        df['EUR'] = df['EUR'].str.replace("EUR", "")
        df['EUR'] = df['EUR'].str.strip()
        df['EUR'] = df['EUR'].str.replace("\', \'\')]", "")
        df['EUR'] = df['EUR'].str.replace("\', \'", "")
        df['EUR'] = df['EUR'].str.replace("\')]", "")
        df_clean = df.loc[df['EUR'] != 'Цена при запитване']
        df_clean['EUR'] = df_clean['EUR'].str.strip()
        df_clean['EUR'] = df_clean['EUR'].str.replace(" ", "")
        df_clean['rooms'] = '{}-стаен'.format(self.no_rooms)
        try:
            df_clean['EUR'] = df_clean['EUR'].astype('int32')
            df_clean['m2'] = df_clean['m2'].astype('int32')
        except:
            print('Check some of the values....')
        df_clean.to_csv('/home/user/filav/imoti project/test_df_{}_staen.csv'.format(self.no_rooms))  # save the df 

url = 'https://www.imot.bg/pcgi/imot.cgi?act=3&slink=9pd2go&f1=1'
test = RealEstate(url = url, no_rooms = 3)
test.analyze()

df_analysis = df_clean.copy()
print(df_analysis.info())  # check the data in the df
df_analysis['EUR'] = df_analysis['EUR'].astype('int32')  # change dtype of EUR columns
df_analysis = df_analysis[df_analysis['EUR'] != 0]

# stats
sns.boxplot(data = df_analysis, x='rooms', y='EUR', width = 0.5)
plt.show()
