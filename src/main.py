import os
import time
from datetime import datetime, timezone, timedelta
from tweet_handler import TweetHandler
from selenium import webdriver
from line_handler import LineHandler
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


URL = os.environ["SCRAPING_TARGET_URL"]
WEEKDAY_LIST = ["月","火","水","木","金","土","日"]
TARGET_MONTH_NUM = 2  # 当月含めて何か月分チェックするか


def exec_single_month(driver, line_handler, tweet_handler):
    year_str = driver.find_element_by_xpath("//*[@id=\"searchCalendar\"]/div/h3/span[1]").text.strip("年")
    month_str = driver.find_element_by_xpath("//*[@id=\"searchCalendar\"]/div/h3/span[2]").text.strip("月")
    for target_date in range(1, 32):
        try:
            date_elem_list = driver.find_elements_by_class_name("date")
            target_date_str = str(target_date)
            for date_elem in date_elem_list:
                if date_elem.text == target_date_str:
                    target_date_elem = date_elem
                    break
            dt = datetime(year=int(year_str), month=int(month_str), day=int(target_date),tzinfo=timezone(timedelta(hours=+9)))
            weekday_str = WEEKDAY_LIST[dt.weekday()]
            print(f"{year_str}/{month_str}/{target_date}({weekday_str})チェック...")
            target_date_elem.click()
            time.sleep(1)
            # view on smart phone
            view_on_sp_str = "//*[@id=\"searchEticket\"]"
            view_on_sp_elem = driver.find_element_by_xpath(view_on_sp_str)
            view_on_sp_elem.click()
            time.sleep(15)
            # 1デーパスポート
            now_on_sale_str = "//*[@id=\"searchResultList\"]/ul/li[1]/div/input"
            now_on_sale_elem = driver.find_element_by_xpath(now_on_sale_str)
            dt_now_utc_aware = datetime.now(timezone(timedelta(hours=9)))
            tweet_handler.post_tweet(f"{year_str}/{month_str}/{target_date}({weekday_str})の1デーパス空いてるよ！\n"
                                     f"{URL}\n\n"
                                     f"※{dt_now_utc_aware.strftime('%Y/%m/%d %H:%M:%S')}時点の情報\n"
                                     f"#ディズニーチケット")
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
    try:
        # > が存在する場合、それをクリックしてreturn
        next_month_button = driver.find_element_by_xpath("//*[@id=\"searchCalendar\"]/div/div/ul/button[2]")
        next_month_button.click()
    except Exception as e:
        print(e)


def main():
    driver = webdriver.Remote(
        command_executor=os.environ["SELENIUM_URL"],
        desired_capabilities=DesiredCapabilities.FIREFOX.copy())
    driver.implicitly_wait(5)
    driver.get(URL)
    line_handler = LineHandler()
    tweet_handler = TweetHandler()
    for i in range(TARGET_MONTH_NUM):
        exec_single_month(driver, line_handler, tweet_handler)
        time.sleep(5)
    driver.quit()


if __name__ == "__main__":
    main()
