from playwright.sync_api import sync_playwright
from requests import post
from colorama import init
from ctypes import windll
from time import sleep
import datetime
import os

WEBHOOK_URL = "DISCORD-WEBHOOK"

class colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

def read_file(file_name: str):
    try:
        accounts = []

        f = open(file_name)
        current_account = None
            
        for line in f:
            if line.strip().startswith("#"):
                continue

            elif "-" in line.strip():
                if current_account:
                    accounts.append(current_account)
                current_account = []

            else:
                if current_account is None:
                    current_account = []
                current_account.append(line.strip())
            
        if current_account:
            accounts.append(current_account)
            
        f.close()
                
        buffer = []
        
        for i in accounts:
            if(len(i) != 3):
                continue
            
            buffer.append(i)
        
        return buffer
    except:
        print(f"Bir hata meydana geldi, {file_name} okunamadı.")
        sleep(2)
        exit()

def spawn_driver(channel_name, token: str, proxy: str):
    
    windll.kernel32.SetConsoleTitleW(f"Twitch Revenue Bot ~ Current Channel: {channel_name} | Başarılı: {succ} | Başarısız: {fail}")

    if(proxy != "proxy"):
        proxy_arr = proxy.split(":")
        proxy_dict = {
            "server": f"http://{proxy_arr[0]}:{proxy_arr[1]}",
            "username": proxy_arr[2],
            "password": proxy_arr[3],
        }
    
    extension_path = os.path.join(os.getcwd(), "webrtc")
    with sync_playwright() as pw:
        if(proxy != "proxy"):
            browser = pw.chromium.launch(
                proxy=proxy_dict,
                headless=False,
                executable_path="C:\Program Files (x86)\chrome-win\chrome.exe",
                args=[
                    f"--disable-extensions-except={extension_path}",
                    f"--load-extension={extension_path}",
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--extensions-on-chrome-urls",
                    "--mute-audio"
                ],
            )
            
            ctx = browser.new_context(
                proxy=proxy_dict,
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
            )
        else:
            browser = pw.chromium.launch(
                headless=False,
                executable_path="C:\Program Files (x86)\chrome-win\chrome.exe",
                args=[
                    f"--disable-extensions-except={extension_path}",
                    f"--load-extension={extension_path}",
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--extensions-on-chrome-urls",
                    "--mute-audio"
                ],
            )
        
            ctx = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
            )
        
        cookie = {
            "domain": ".twitch.tv",
            "expirationDate": 1755440604,
            "hostOnly": False,
            "httpOnly": False,
            "name": "auth-token",
            "path": "/",
            "sameSite": "None",
            "secure": True,
            "session": False,
            "storeId": "0",
            "value": token,
        }
        
        ctx.add_cookies([cookie])
        extension_id = '"bppamachkoflopbagkdoflbgfjflfnfl"'
        page = ctx.new_page()

        page.goto("chrome://extensions")
        page.evaluate(f"chrome.developerPrivate.updateExtensionConfiguration({{extensionId: {extension_id}, incognitoAccess: true}})")

        # prime subs = //*[@id="root"]/div[3]/div/div/div[2]/div/main/div/div[3]/div/div/div/div[3]/div/div/div[5]/div/div[1]/div/div/div[2]/div/div[2]/div/div[2]/div/div/div[2]/h5
        # total revenue //*[@id="root"]/div[3]/div/div/div[2]/div/main/div/div[3]/div/div/div/div[3]/div/div/div[5]/div/div[1]/div/div/div[2]/div/div[1]/div[1]/h2
        # status //*[@id="root"]/div[3]/div/div/div[2]/div/main/div/div[3]/div/div/div/div[3]/div/div/div[3]/div[2]/div[2]/div/div[2]/div/div/div[2]/span
        # check data-a-target="tw-core-button-label-text"

        today = datetime.date.today()

        end_time = today.strftime('%Y-%m-%d')
        start_time = today.replace(day=1) - datetime.timedelta(days=1)
        start_time = start_time.replace(day=1).strftime('%Y-%m-%d')

        page.goto(f"https://dashboard.twitch.tv/u/{channel_name}/analytics/revenue-earnings?end={end_time}&start={start_time}", wait_until="load")
        
        try:
            not_accesable = True if len(page.query_selector('[data-a-target="core-error-message"]').text_content()) > 30 else False
            if (not_accesable):
                print(colors.RED + f"{channel_name}, Given token is invalid for this channel!" + colors.ENDC)
                ctx.close()
                browser.close()
                return
            try:
                post(url=WEBHOOK_URL, json={"content": f"||**{channel_name}:**\n**Invalid Token**||"})
            except:
                pass
        except:
            pass
        
        try:
            total_revenue_locator = ".total-revenue-title+h2"
            total_revenue_element = page.wait_for_selector(total_revenue_locator, timeout=2000)
            total_revenue = total_revenue_element.text_content()
        except:
            try:
                total_revenue_element = page.wait_for_selector(total_revenue_locator, timeout=2000)
                total_revenue = total_revenue_element.text_content()
            except:
                total_revenue = "0"

        try:
            prime_revenue_locator = ".CoreText-sc-1txzju1-0.feJdGm"
            prime_revenue_element = page.wait_for_selector(prime_revenue_locator, timeout=2000)
            prime_revenue = prime_revenue_element.text_content()
        except:
            try:
                prime_revenue_element = page.wait_for_selector(prime_revenue_locator, timeout=2000)
                prime_revenue = prime_revenue_element.text_content()
            except:
                prime_revenue = "0"
        
        page.goto(f"https://dashboard.twitch.tv/u/{channel_name}/analytics/revenue-payouts", wait_until="load")
        

        status = False
        try:
            page.wait_for_selector('//span[text()="Eligible"]', timeout=10000000)
            status = True
        except:
            try:
                page.wait_for_selector('//span[text()="Есть право на выплату"]', timeout=10000000)
                status = True
            except:
                try:
                    page.wait_for_selector('//span[text()="Uygun"]', timeout=1000000)
                    status = True
                except:
                       pass

        if(status):
            status = "Eligible"
        else:
            status = "On Hold"

        print(status)
        
        print(colors.GREEN + f"{channel_name}:\nTotal Revenue: {total_revenue}, Prime Revenue: {prime_revenue}, Status: {status}\n" + colors.ENDC)
        
        try:
            post(url=WEBHOOK_URL, json={"content": f"```diff\n+ {channel_name}\nTotal Revenue: \n- {total_revenue}\nPrime Revenue: \n- {prime_revenue}\n+ Status: {status}\n```"})
        except:
            pass
        
        ctx.close()
        browser.close()
        
if __name__ == "__main__":
    init()
    
    inputs = read_file("revenue.txt")
    
    succ = 0
    fail = 0

    for index, array in enumerate(inputs, start=1):
        if (":" in array[2]) or array[2] == "proxy":
            spawn_driver(array[0], array[1], array[2])
            if index != len(inputs):
                print(f"Sıradaki Hesap: {index+1}")
            else:
                print("\nTüm hesaplar işlendi.\n")
            succ += 1
        else:
            fail += 1

    print("\n" + colors.GREEN + f"Başarılı Hesap: {succ}" + colors.ENDC)
    print(colors.RED + f"Başarısız Hesap: {fail}" + colors.ENDC)
 
    input()
