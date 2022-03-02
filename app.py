import random
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from settings import password, login, users_per_competitor


class Login:
    """ Sign in to Instagram, with the data from the settings.py file """
    def __init__(self, login_info, password_info):
        self.login_info = login_info
        self.password_info = password_info
        mobile_emulation = {"deviceName": "iPhone X"}
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        self.browser = webdriver.Chrome(options=chrome_options)

    def close_browser(self):
        self.browser.close()
        self.browser.quit()

    def login(self):
        self.open_instagram()
        self.go_to_login_page()
        self.enter_login()
        self.enter_password()
        self.press_enter()

    def open_instagram(self):
        time.sleep(random.randrange(3, 5))
        self.browser.get('https://www.instagram.com/')
        time.sleep(random.randrange(3, 5))

    def go_to_login_page(self):
        door = self.browser.find_element(By.XPATH,
                                         "/html/body/div[1]/section/main/article/div/div/div/div[3]/button[1]")
        door.click()
        time.sleep(random.randrange(2, 3))

    def enter_login(self):
        login_form = self.browser.find_element(By.NAME, "username")
        login_form.clear()
        login_form.send_keys(login)
        time.sleep(random.randrange(2, 4))

    def enter_password(self):
        password_form = self.browser.find_element(By.NAME, "password")
        password_form.clear()
        password_form.send_keys(password)

    def press_enter(self):
        password_form = self.browser.find_element(By.NAME, "password")
        password_form.send_keys(Keys.ENTER)
        time.sleep(10)


class Subscribe:
    """ Receives a list of subscribers for specified competitors
    from the file settings.py and subscribes to the received list """

    def __init__(self, pass_the_browser):
        self.competitor_profile_id = check_for_matches()
        self.browser = pass_the_browser.browser
        self.list_of_competitor_subscribers = []

    def get_list_to_subscribe(self):
        for competitor in self.competitor_profile_id:
            self.browser.get(f"https://www.instagram.com/{competitor}/")
            time.sleep(5)
            self.view_subscribers()
            for scroll in range(1, number_need_to_scroll()):
                self.render_subscribers_popup()
            self.list_of_competitor_subscribers += self.get_list_of_competitor_subscribers(competitor, login)
            write_competitor_done_to_file(competitor)

    def subscribe(self):
        for user_id in self.list_of_competitor_subscribers:
            self.browser.get(user_id)
            user_post_id = self.render_user_post_id()
            if not user_post_id:
                # Перевірка чи це не приватний профіль
                time.sleep(random.randrange(2, 4))
            elif self.xpath_exists("//*[text()='Редагувати профіль']"):
                # Перевірка чи це моя сторінка
                time.sleep(random.randrange(2, 4))
            elif self.xpath_exists("/html/body/div[5]/div/div/div/div[3]/button[2]"):
                # Перевірка чи це не вспливаючий Поп-ап Інстаграму
                time.sleep(random.randrange(2, 4))
            elif self.xpath_exists("//*[text()='Повідомлення']"):
                # Перевірка, чи уже підписаний на цільову сторінку.
                with open('already_done_user.txt', 'a') as already_done_user:
                    already_done_user.write(user_id + '\n')
                time.sleep(random.randrange(2, 4))
            elif self.xpath_exists("/html/body/div[1]/section/nav[1]/div/div/header/div/div[2]/a/svg"):
                # Перевірка чи це не головна сторінка інстаграм
                time.sleep(random.randrange(2, 4))
            else:
                self.click_follow()
                self.browser.get(user_post_id[0])
                self.like_post()
                with open('already_done_user.txt', 'a') as already_done_user:
                    already_done_user.write(user_id + '\n')
                print('Successfully subscribed to - ' + user_id)
                time.sleep(random.randrange(5, 10))
                # time.sleep(random.randrange(80, 90))

    def view_subscribers(self):
        time.sleep(random.randrange(3, 5))
        subscribers_button = self.browser.find_element(By.XPATH, "/html/body/div[1]/section/main/div/ul/li[2]/a")
        subscribers_button.click()
        time.sleep(random.randrange(2, 3))

    def render_subscribers_popup(self):
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.randrange(2, 3))

    def get_list_of_competitor_subscribers(self, enemy, user):
        hrefs = self.browser.find_elements(By.TAG_NAME, 'a')
        list_to_ignore = ['https://www.instagram.com/explore/',
                          'https://www.instagram.com/',
                          'https://www.instagram.com/accounts/activity/',
                          f'https://www.instagram.com/{user}/',
                          f'https://www.instagram.com/{enemy}/']
        done_user = [line.rstrip('\n') for line in open('already_done_user.txt')]
        subscribers_id = [item.get_attribute('href') for item in hrefs]
        subscribers_id = set(subscribers_id) - set(list_to_ignore) - set(done_user)
        print(subscribers_id)
        return subscribers_id

    def render_user_post_id(self):
        find_post = self.browser.find_elements(By.TAG_NAME, 'a')
        render_post = [item.get_attribute('href') for item in find_post if "/p/" in item.get_attribute('href')]
        return render_post

    def click_follow(self):
        time.sleep(random.randrange(3, 4))
        follow_button = self.browser.find_element(By.XPATH, "//*[text()='Стежити']")
        follow_button.click()
        time.sleep(random.randrange(1, 2))

    def like_post(self):
        like_post = self.browser.find_element(By.XPATH, "/html/body/div[1]/section/main/div/div/article"
                                                        "/div/div[ "
                                                        "3]/div/div/section[ "
                                                        "1]/span[1]/button")
        like_post.click()

    def xpath_exists(self, url):
        try:
            self.browser.find_element(By.XPATH, url)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist


def check_for_matches():
    not_worked_out = [line.rstrip('\n') for line in open('competitor.txt')]
    worked_out = [line.rstrip('\n') for line in open('competitor_done.txt')]
    list_of_competitor = set(not_worked_out) - set(worked_out)
    list_of_competitor = list(list_of_competitor)
    return list_of_competitor


def number_need_to_scroll():
    number_scrolls = users_per_competitor // 12
    return number_scrolls


def write_competitor_done_to_file(competitor):
    open_enemy_done_list = open('competitor_done.txt', 'a')
    open_enemy_done_list.write(competitor + '\n')
    open_enemy_done_list.close()


if __name__ == "__main__":
    my_bot = Login(login, password)
    my_bot.login()
    my_bot = Subscribe(my_bot)
    my_bot.get_list_to_subscribe()
    my_bot.subscribe()
