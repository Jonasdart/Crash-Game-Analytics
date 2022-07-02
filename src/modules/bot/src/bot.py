import os
import logging
from datetime import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.bot.src.utils.configs import (
    BET_PERCENT,
    EMAIL,
    MAX_BET,
    MIN_PURSE,
    MULTI_LOSE,
    MULTI_ODD,
    PASSWORD,
    SAQUE_AMOUNT,
    SAQUE_CPF,
    SAQUE_PIX,
    SAQUE_TITULAR,
    SAQUE_WHATSAPP,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s-%(levelname)s: %(message)s")


keys = Keys()


class Bet:
    def __init__(self):
        self.driver = webdriver.Chrome(chrome_options=self.__load_chrome_options()
        )
        self.driver.maximize_window()
        self.purse_value = 0.0
        self.last_result_is_win = 1

    def __load_chrome_options(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        return chrome_options

    def _win(self):
        logging.info(f"Win")
        self.last_result_is_win = 1

    def _lose(self):
        logging.info(f"Lose")
        self.last_result_is_win = 0

    def login(self):
        self.driver.get("https://betfiery.com/")
        WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "ant-modal-close"))
        )
        self.driver.find_element(By.CLASS_NAME, "ant-modal-close").send_keys(
            keys.ESCAPE
        )
        self.driver.find_element(By.CLASS_NAME, "loginBtn").click()

        self.driver.find_element(By.ID, "basic_email").send_keys(EMAIL)
        self.driver.find_element(By.ID, "basic_password").send_keys(PASSWORD)
        self.driver.find_element(By.CLASS_NAME, "logInActionBtn").click()

        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "/div/div/div/span[2]/div/h3")
                )
            )
            WebDriverWait(self.driver, 5).until_not(
                EC.visibility_of_element_located(
                    (By.XPATH, "/div/div/div/span[2]/div/h3")
                )
            )
        except:
            pass

        return True

    def open_crash_game(self):
        self.driver.get("https://betfiery.com/crashGame")
        # self.driver.find_elements(By.CLASS_NAME, 'topMenu_col_2__mZKnh')[0].click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located(
                (By.CLASS_NAME, "roundButton_roundButton__bUaXz")
            )
        )
        self.driver.find_elements(By.CLASS_NAME, "roundButton_roundButton__bUaXz")[
            -1
        ].click()
        self.driver.find_elements(By.CLASS_NAME, "roundButton_roundButton__bUaXz")[
            -1
        ].click()

    def acquire_purse_value(self):
        xpath = '//*[@id="root"]/div/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/div[3]/div[2]/label/p'
        purse_value = self.driver.find_element(By.XPATH, xpath)
        purse_value = purse_value.text.split("R$ ")[-1]

        return float(purse_value)

    def get_next_bet_value(self) -> int:
        logging.info("-" * 10)
        logging.info(f"Banca: R$ {self.purse_value}")
        if self.last_result_is_win:
            return self.purse_value * (BET_PERCENT * 0.01)

        return (self.purse_value * (BET_PERCENT * 0.01)) * MULTI_LOSE

    def previne_critical_lose(self, bet_value):
        if bet_value > MAX_BET:
            logging.info("CRITICAL LOSE PREVINE SET BET VALUE TO DEFAULT")
            bet_value = MAX_BET

        return bet_value

    def round_bet_value(self, value):
        value = int(str(value).split(".")[0])
        if value == 0:
            value = 1

        return value

    def valide_purse_state(self, value):
        if self.purse_value > value:
            return self._lose()
        if self.purse_value < value:
            return self._win()

        return

    def saque(self):
        if self.purse_value >= (SAQUE_AMOUNT + MIN_PURSE):
            logging.info(f"-- Aguardando saque de {SAQUE_AMOUNT} --")
            now = datetime.now()
            if now.hour > 19:
                sleep_time = 23 - now.hour + 6
                sleep(sleep_time * 3600)
            if now.hour < 6:
                sleep_time = 6 - now.hour
                sleep(sleep_time * 3600)

            self.driver.find_element(
                By.CLASS_NAME, "betFiery-svgIcon head-wallet"
            ).click()
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(
                    (
                        By.CLASS_NAME,
                        "roundModal_RadioButton__UWsUG roundModal_activeRadioButton_withdraw__4zg4T",
                    )
                )
            )

            self.driver.find_element(
                By.CLASS_NAME,
                "roundModal_RadioButton__UWsUG roundModal_activeRadioButton_withdraw__4zg4T",
            ).click()
            self.driver.find_element(By.ID, "withdraw_w_amount").insert(SAQUE_AMOUNT)
            self.driver.find_element(By.ID, "withdraw_accountname").insert(
                SAQUE_TITULAR
            )
            self.driver.find_element(By.ID, "withdraw_taxid").insert(SAQUE_CPF)
            self.driver.find_element(By.ID, "withdraw_phone").insert(SAQUE_WHATSAPP)
            self.driver.find_element(By.ID, "withdraw_pixkey").insert(SAQUE_PIX)

            self.driver.find_element(
                By.CLASS_NAME, "ant-btn ant-btn-primary ant-btn-lg"
            ).click()
            sleep(4)

    def bet(self):
        bet_status = "Wait"
        while True:
            bet_button = self.driver.find_element(
                By.CLASS_NAME, "betButton_betBtnText__oEDHG"
            )
            if bet_status == "Wait":
                if bet_button.text.upper() == "APOSTA":
                    actual_purse_value = self.acquire_purse_value()
                    self.valide_purse_state(actual_purse_value)
                    self.purse_value = actual_purse_value

                    self.saque()

                    bet_amount = self.round_bet_value(self.get_next_bet_value())
                    self.send_bet(bet_amount)
                    bet_status = "Bet"
            elif bet_status == "Bet":
                if bet_button.text.upper() != "APOSTA":
                    bet_status = "Wait"

            sleep(1)

    def send_bet(self, value):
        value = self.previne_critical_lose(value)
        logging.info(f"Apostando {value} em {MULTI_ODD}x")
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "betButton_betBtnText__oEDHG"), "Aposta"
            )
        )
        self.driver.find_element(By.ID, "betAmountInput").clear()
        self.driver.find_element(By.ID, "betAmountInput").send_keys(value)
        self.driver.find_element(By.ID, "cashOutAtInput").clear()
        self.driver.find_element(By.ID, "cashOutAtInput").send_keys(str(MULTI_ODD))
        self.driver.find_element(By.CLASS_NAME, "betButton_betBtnText__oEDHG").click()
        logging.info("Apostado")

    def start(self):
        self.login()
        self.open_crash_game()
        self.purse_value = self.acquire_purse_value()
        self.bet()


if __name__ == "__main__":
    bot = Bet()
    bot.start()
