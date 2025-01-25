import time
import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

class Config:# 配置登录页面和登录状态检查接口
    LOGIN_URL = "https://kyfw.12306.cn/otn/resources/login.html"
    CHECK_LOGIN_URL = "https://kyfw.12306.cn/otn/login/checkUser"
class LoginModule:
    """负责登录功能"""
    def __init__(self):
        self.session = requests.Session()  # 用于检查登录状态的会话
        self.driver = None  # 浏览器 WebDriver

    def setup_driver(self):
        """设置并启动 Edge 浏览器"""
        service = Service(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=service)

    def login(self):
        """打开登录页面并等待用户登录"""
        self.driver.get(Config.LOGIN_URL)
        print("请在浏览器中完成登录...")
        while not self.check_login_status():  # 循环检查登录状态
            time.sleep(10)
            print("登录未完成，请稍等...")
        print("登录成功！")

    def check_login_status(self):
        """通过检查接口判断是否已登录"""
        try:
            response = self.session.post(Config.CHECK_LOGIN_URL, timeout=10)
            return response.json().get("status") == "success"  # 登录成功返回 True
        except Exception as e:
            print(f"检查登录状态失败：{e}")
            return False

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()

class TicketModule:# 负责车票查询功能
    def __init__(self, driver):
        self.driver = driver

    def search_tickets(self, from_station, to_station, date):
        """查询车票信息"""
        self.driver.get(Config.LOGIN_URL)  # 访问查询页面
        time.sleep(3)  # 等待页面加载

        # 输入出发地
        self.driver.find_element("id", "fromStationText").click()
        self.driver.find_element("xpath", f"//li[contains(text(), '{from_station}')]").click()

        # 输入目的地
        self.driver.find_element("id", "toStationText").click()
        self.driver.find_element("xpath", f"//li[contains(text(), '{to_station}')]").click()

        # 输入日期并查询
        self.driver.find_element("id", "train_date").send_keys(date)
        self.driver.find_element("id", "query_ticket").click()
        time.sleep(5)  # 等待查询结果加载

        # 获取车票信息
        tickets = self.driver.find_elements("xpath", "//tr[@datatran]")
        return [ticket.text.split("\n") for ticket in tickets]

class BookingModule:
    """负责提交订单功能"""
    @staticmethod
    def submit_order(ticket):
        """提交订单"""
        print(f"提交订单：{ticket}")
        return {"status": "success", "order_id": "12345"}  # 模拟返回订单ID

class PaymentModule:
    """负责支付功能"""
    @staticmethod
    def pay_order(order_id):
        """支付订单"""
        print(f"支付订单：{order_id}")
        return True  # 模拟支付成功

class Notify:
    """负责发送通知功能"""
    @staticmethod
    def send_notification(message):
        """发送通知"""
        print(f"通知：{message}")

if __name__ == "__main__":
    # 模块实例化
    login = LoginModule()
    try:
        # 设置浏览器并登录
        login.setup_driver()
        login.login()

        # 通知登录成功
        notify = Notify()
        notify.send_notification("登录成功！")

        # 查询车票
        query = TicketModule(login.driver)
        tickets = query.search_tickets("北京", "上海", "2025-01-10")
        # 筛选符合条件的票
        available_tickets = [ticket for ticket in tickets if "硬卧" in ticket]

        if available_tickets:
            # 提交订单
            booking = BookingModule()
            result = booking.submit_order(available_tickets[0])
            if result.get("status") == "success":
                notify.send_notification("抢票成功！请及时支付！")

                # 支付订单
                payment = PaymentModule()
                if payment.pay_order(result["order_id"]):
                    notify.send_notification("支付成功！")
                else:
                    notify.send_notification("支付失败，请重试！")
    except Exception as e:
        print(f"程序运行中出错：{e}")
    finally:
        # 关闭浏览器
        login.close()
