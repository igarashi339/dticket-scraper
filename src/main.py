import os
import time
from datetime import datetime, timezone
from tweet_handler import TweetHandler
from selenium import webdriver
from line_handler import LineHandler
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


URL = os.environ["SCRAPING_TARGET_URL"]


def exec_single_month(driver, line_handler, tweet_handler):
    # month
    month_str = driver.find_element_by_xpath("//*[@id=\"searchCalendar\"]/div/h3/span[2]").text.strip("月")
    for target_date in range(1, 32):
        try:
            date_elem_list = driver.find_elements_by_class_name("date")
            target_date_str = str(target_date)
            for date_elem in date_elem_list:
                if date_elem.text == target_date_str:
                    target_date_elem = date_elem
                    break
            print(f"{month_str}月{target_date}日チェック...")
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
            dt_now_utc_aware = datetime.datetime.now(datetime.timezone.utc)
            tweet_handler.post_tweet(f"{month_str}月{target_date}日の1デーパスポートが空いたよ！\n{URL}\n\n"
                                     f"※{dt_now_utc_aware.strftime('%Y/%m/%d/ %H:%M:%S')}時点の情報です")
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
        return False
    return True


def exec_single_date(driver, line_handler):
    start_time = time.time()
    elapsed_time = 0
    MAX_TIME_SECOND = 50 * 60  # 処理を打ち切る時間[秒]
    while elapsed_time < MAX_TIME_SECOND:
        elapsed_time = time.time() - start_time
        try:
            # 2021/12/18
            driver.find_element_by_xpath("//*[@id=\"searchCalendar\"]/div/div/ul/div/div/li[1]/div/table/tbody/tr[3]/td[6]/a/span[1]").click()
            time.sleep(1)
            driver.find_element_by_xpath("//*[@id=\"searchEticket\"]").click()
            time.sleep(15)
            driver.find_element_by_xpath("//*[@id=\"searchResultList\"]/ul/li[1]/div/input")
            line_handler.broadcast(f"12/18(土)の1デーパスポートがとれそう！\n{URL}")
        except Exception as e:
            print(e)
        time.sleep(10)
    return


def main():
    driver = webdriver.Remote(
        command_executor=os.environ["SELENIUM_URL"],
        desired_capabilities=DesiredCapabilities.FIREFOX.copy())
    driver.implicitly_wait(5)
    driver.get(URL)
    line_handler = LineHandler()
    tweet_handler = TweetHandler()
    # exec_single_date(driver, line_handler)
    should_continue = True
    while should_continue:
        should_continue = exec_single_month(driver, line_handler, tweet_handler)
        time.sleep(5)
    driver.quit()


if __name__ == "__main__":
    main()
