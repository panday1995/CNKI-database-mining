from collections import Iterable
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from time import sleep
import selenium.webdriver.support.expected_conditions as EC
import pandas as pd

browser = webdriver.Chrome(r"E:/BaiduYunDownload/chromedriver")
browser.get(r"http://data.cnki.net/ValueSearch/Index?datatype=year&ky=GDP")

def find_table(indicator, region, year):

    browser.find_element_by_name("IndicateName").clear()
    browser.find_element_by_name("IndicateName").send_keys(indicator)
    browser.find_element_by_name("IndicateRegion").clear()
    browser.find_element_by_name("IndicateRegion").send_keys(region)
    browser.find_element_by_name("StartYear").send_keys(year)
    browser.find_element_by_name("EndYear").send_keys(year)
    element = browser.find_element_by_id("AdvancedSearch")
    browser.execute_script(
        "arguments[0].click();", element
    )  # arguments[0], element means passing element into arguments[0] to execute in Javascript
    xpath = "/html/body/div[1]/div[3]/div[1]/div/div[2]/table/tbody/tr"
    sleep(20)

    ls = []
    try:
        table = browser.find_elements_by_xpath(xpath)
        for tr in table:
            tds = tr.find_elements_by_tag_name("td")
            ls.append([td.text for td in tds])
    except EC.StaleElementReferenceException:
        table = browser.find_elements_by_xpath(xpath)
        for tr in table:

            tds = tr.find_elements_by_tag_name("td")
            ls.append([td.text for td in tds])
    table_df = pd.DataFrame(ls)
    return table_df
    
 def data_collect(
    indicator_list, region_list, year_range, year_filter=None, unit_filter=None
):
    city_ls = []
    year_ls = []
    indicator_ls = []
    for city in region_list:
        for year in year_range:
            for indicator in indicator_list:
                indicator_ls.append(find_table(indicator, city, str(year)))
            indicator_data = pd.concat(indicator_ls)
            year_ls.append(indicator_data)
        year_data = pd.concat(year_ls)
        city_ls.append(year_data)
    total_df = pd.concat(city_ls)
    try:
        if isinstance(year_filter, Iterable):
            total_df_screened = total_df[
                (total_df[2].str.contains("|".join(year_filter)))
                & (total_df[6].str.contains(unit_filter))
            ].iloc[:, 2:7]
        else:
            total_df_screened = total_df[
                (total_df[2].str.contains(year_filter))
                & (total_df[6].str.contains(unit_filter))
            ].iloc[:, 2:7]
    except:
        total_df_screened = total_df
    return total_df_screened
    
year_range = list(range(2005, 2019))
year_filter = [str(i) for i in year_range]
province = [
    "北京",
    "天津",
    "河北",
    "山西",
    "内蒙古",
    "辽宁",
    "吉林",
    "黑龙江",
    "上海",
    "江苏",
    "浙江",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖北",
    "湖南",
    "广东",
    "广西",
    "海南",
    "重庆",
    "四川",
    "贵州",
    "云南",
    "陕西",
    "甘肃",
    "青海",
    "宁夏",
    "新疆",
]
indicator_list = ["能源消费总量"]

data_df = data_collect(
    indicator_list, province, year_range, year_filter=year_filter, unit_filter="标准煤"
)

data_df_screened = data_df.drop_duplicates()

path = (
    r"E:\tencent files\chrome Download\Research\DEA\DEA_carbon market\Data_collection\\"
)

data_df_screened.to_excel(path + indicator_list[0] + ".xlsx")
