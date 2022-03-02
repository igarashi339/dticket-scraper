import os
import time
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from tweet_handler import TweetHandler
from selenium import webdriver
from line_handler import LineHandler
from db_handler import DBHandler
import urllib
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


TARGET_URL = os.environ["SCRAPING_TARGET_URL"]
WEEKDAY_LIST = ["月","火","水","木","金","土","日"]
EXEC_PER_HOUR = 2 # 何回転させるか
RETRY_NUM = 5


def get_target_date_obj_list():
    """
    クローリング対象のdatetimeオブジェクトのリストを取得する。
    本日から2か月間を対象とする。
    """
    current_date = datetime.now(timezone(timedelta(hours=9)))
    end_date = current_date + relativedelta(months=2) - timedelta(days=2)
    target_date_list = [current_date]
    should_continue = True
    while should_continue:
        next_date = current_date + timedelta(days=1)
        current_date = next_date
        target_date_list.append(next_date)
        if next_date > end_date:
            should_continue = False
    return target_date_list


def fetch_single_date_ticket_info(driver, target_date_obj):
    target_date_str = target_date_obj.strftime('%Y%m%d')
    param_dict = {
        "parkTicketGroupCd": "020",
        "numOfAdult": "2",
        "numOfJunior": "0",
        "numOfChild": "0",
        "parkTicketSalesForm": "1",
        "useDays": "1",
        "route": "1",
        "selectParkDay1": "01",
        "useDateFrom": target_date_str
    }
    param = urllib.parse.urlencode(param_dict)
    driver.get(TARGET_URL + "?" + param)
    time.sleep(8)

    for i in range(RETRY_NUM):
        tdl_str = driver.find_element_by_xpath("//*[@id=\"search-ticket-group\"]/div/section/div[2]/section[1]/div[1]/div/ul/li[1]/span").text
        tds_str = driver.find_element_by_xpath("//*[@id=\"search-ticket-group\"]/div/section/div[2]/section[1]/div[1]/div/ul/li[2]/span").text
        if tdl_str != "" and tds_str != "":
            break
        time.sleep(5)
    if tdl_str == "" or tds_str == "":
        raise Exception(f"{RETRY_NUM}回トライしましたが指定の要素を取得できませんでした。")
    tdl_is_available = False
    tds_is_available = False
    if "運営時間" in tdl_str:
        tdl_is_available = True
    if "運営時間" in tds_str:
        tds_is_available = True
    print("------------------")
    print(f"target_date: {target_date_str}")
    print(f"tdl_str: {tdl_str}")
    print(f"tds_str: {tds_str}")
    print(f"tdl_is_available: {tdl_is_available}")
    print(f"tds_is_available: {tds_is_available}")
    return tdl_is_available, tds_is_available


def get_should_tweet(db_handler, target_datetime_obj, tdl_is_available, tds_is_available):
    """
    スクレイピング結果を受けてTweetするかを決定する。
    """
    holiday_both_flag = False  # 土日海陸
    holiday_land_flag = False  # 土日陸
    holiday_sea_flag = False  # 土日海
    weekday_both_flag = False  # 平日海陸
    weekday_str = WEEKDAY_LIST[target_datetime_obj.weekday()]
    prev_land_available = db_handler.select_from_dticket_status(target_datetime_obj, "land")
    prev_sea_available = db_handler.select_from_dticket_status(target_datetime_obj, "sea")
    land_flag = (not prev_land_available and tdl_is_available)
    sea_flag = (not prev_sea_available and tds_is_available)
    both_flag = land_flag or sea_flag
    if weekday_str == "土" or weekday_str == "日":
        holiday_land_flag = land_flag
        holiday_sea_flag = sea_flag
        holiday_both_flag = both_flag
    else:
        weekday_both_flag = both_flag
    return holiday_land_flag, holiday_sea_flag, holiday_both_flag, weekday_both_flag


def post_tweet(tweet_handler, target_date_obj, tdl_is_available, tds_is_available, holiday_land_tweet_flag,
               holiday_sea_tweet_flag, holiday_both_tweet_flag, weekday_both_tweet_flag, counter):
    dt_now_utc_aware = datetime.now(timezone(timedelta(hours=9)))
    weekday_str = WEEKDAY_LIST[target_date_obj.weekday()]
    tdl_available_str = "〇" if tdl_is_available else "×"
    tds_available_str = "〇" if tds_is_available else "×"
    param_date = format(target_date_obj, '%Y-%m-%d')
    if holiday_both_tweet_flag:
        param = f"land={param_date}&sea={param_date}"
        tweet_handler.post_tweet(f"{format(target_date_obj, '%Y/%m/%d')}({weekday_str})の1デーパス空いてるよ！\n"
                                 f"ランド{tdl_available_str} シー{tds_available_str}\n"
                                 f"https://tdr-plan.com/ticket?{param}\n"
                                 f"※{dt_now_utc_aware.strftime('%Y/%m/%d %H:%M:%S')}時点の情報\n"
                                 f"#ディズニー #ディズニーチケット")
    if weekday_both_tweet_flag:
        param = f"land={param_date}&sea={param_date}"
        tweet_handler.post_tweet_weekday(f"{format(target_date_obj, '%Y/%m/%d')}({weekday_str})の1デーパス空いてるよ！\n"
                                         f"ランド{tdl_available_str} シー{tds_available_str}\n"
                                         f"https://tdr-plan.com/ticket?{param}\n"
                                         f"※{dt_now_utc_aware.strftime('%Y/%m/%d %H:%M:%S')}時点の情報\n"
                                         f"#ディズニー #ディズニーチケット")


def main():
    driver = webdriver.Remote(
            command_executor=os.environ["SELENIUM_URL"],
            desired_capabilities=DesiredCapabilities.FIREFOX.copy())
    driver.implicitly_wait(5)
    # line_handler = LineHandler()
    tweet_handler = TweetHandler()
    db_handler = DBHandler()
    target_date_obj_list = get_target_date_obj_list()
    for counter in range(EXEC_PER_HOUR):
        for target_datetime_obj in target_date_obj_list:
            target_datetime_str = format(target_datetime_obj, '%Y/%m/%d')
            try:
                tdl_is_available, tds_is_available = fetch_single_date_ticket_info(driver, target_datetime_obj)
            except Exception as e:
                print(f"クローリングに失敗しました: {target_datetime_str}")
                print(e)
                continue
            holiday_land_flag, holiday_sea_flag, holiday_both_flag, weekday_both_flag \
                = get_should_tweet(db_handler, target_datetime_obj, tdl_is_available, tds_is_available)
            db_handler.update_dticket_status_record(target_datetime_obj, "land", tdl_is_available)
            db_handler.update_dticket_status_record(target_datetime_obj, "sea", tds_is_available)
            try:
                if holiday_land_flag or holiday_sea_flag or holiday_both_flag or weekday_both_flag:
                    post_tweet(tweet_handler,
                               target_datetime_obj,
                               tdl_is_available,
                               tds_is_available,
                               holiday_land_flag,
                               holiday_sea_flag,
                               holiday_both_flag,
                               weekday_both_flag,
                               counter)
            except Exception as e:
                print(f"Tweetの投稿に失敗しました： {target_datetime_str}")
                print(e)
                continue
            time.sleep(2)
    driver.quit()


if __name__ == "__main__":
    main()





