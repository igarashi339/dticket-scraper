import os
import time
from selenium import webdriver
from line_handler import LineHandler
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options


URL = os.environ["SCRAPING_TARGET_URL"]


def exec_single_day(driver, line_handler, page, row, col):
    # month
    month_str = driver.find_element_by_xpath("//*[@id=\"searchCalendar\"]/div/h3/span[2]").text
    # day
    day_str = f"//*[@id=\"searchCalendar\"]/div/div/ul/div/div/li[{page}]/div/table/tbody/tr[{row}]/td[{col}]/a/span[1]"
    day_elem = driver.find_element_by_xpath(day_str)
    day_str = day_elem.text + "日"
    day_elem.click()
    time.sleep(1)
    print(f"{month_str}{day_str}チェック...")
    # view on smart phone
    view_on_sp_str = "//*[@id=\"searchEticket\"]"
    view_on_sp_elem = driver.find_element_by_xpath(view_on_sp_str)
    view_on_sp_elem.click()
    time.sleep(15)
    # 1デーパスポート
    now_on_sale_str = "//*[@id=\"searchResultList\"]/ul/li[1]/div/input"
    now_on_sale_elem = driver.find_element_by_xpath(now_on_sale_str)
    line_handler.broadcast(f"{month_str}{day_str}の1デーパスポートがとれそう！\n{URL}")
    # tdl
    # "//*[@id=\"search-ticket-group\"]/div/section/div[2]/section[1]/div[1]/div/ul/li[1]/button"
    # tds
    # "//*[@id=\"search-ticket-group\"]/div/section/div[2]/section[1]/div[1]/div/ul/li[2]/button"
    return


def main():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Remote(
        command_executor=os.environ["SELENIUM_URL"],
        options=options,
        desired_capabilities=DesiredCapabilities.FIREFOX.copy())
    driver.implicitly_wait(5)
    driver.get(URL)
    line_handler = LineHandler()
    for page in [1, 2, 3, 4]:
        for row in [1, 2, 3, 4, 5]:
            for col in [1, 2, 3, 4, 5, 6, 7]:
                try:
                    exec_single_day(driver, line_handler, page, row, col)
                except Exception as e:
                    print(e)
                    time.sleep(1)
    driver.quit()


if __name__ == "__main__":
    main()
