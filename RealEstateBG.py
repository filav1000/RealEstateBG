from scrapy import Selector
import requests
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class RealEstate:
    def __init__(self, url, no_rooms):
        self.url = url
        self.no_rooms = no_rooms

    def analyze(self):
        get_page_numbers = requests.get(self.url)  # read the webpage
        get_page_numbers.encoding = get_page_numbers.apparent_encoding  # encoding
        page_nums_txt = get_page_numbers.text  # response to text
        page_nums = re.findall(r'(Страница\s\d+\sот\s\d+)', page_nums_txt)  # regex to look for the string with number of pages
        pages = int(page_nums[0][-2:])
        print(pages)
        
        price_pattern = r'(\d+\s\d+\sEUR)|(Цена при запитване)'  # или 000 000 eur или Цена при запитване
        area_pattern = r'(\d+\sкв.м)'  #търси "кв.м" в текста към обявата
        prices_all = []
        area_all = []
        prices_all_new = []
        xpath = '//td[contains(text(), "кв.м")]'
        xpath_prices = '//div[contains(@class, "price")]'
        area_modified = []
        prices_final = []
        
        for i in range(1,pages + 1):
            imoti = requests.get(str(self.url[:-1] + '{}').format(i))  # итератор за минаваме през всички страници
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
        
        df = pd.DataFrame(data=[area_modified, prices_final]).T
        df.columns = ['m2', 'EUR']
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
        df_clean.to_csv('/home/user/filav/imoti project/test_df_{}_staen.csv'.format(self.no_rooms))