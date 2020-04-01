import requests
import os
from collections import namedtuple
import asyncio
import random,time
from pyppeteer import launch
input_time_random=random.randint(1,500)
error=''
def screen_size():
    import tkinter
    tk=tkinter.Tk()
    width=tk.winfo_screenwidth()
    height=tk.winfo_screenheight()
    tk.quit()
    return width,height
async def main():
    print(111111111)
    #'headless': True 不显示浏览器        False显示浏览器
    # browser=await launch({'headless': True, 'args': ['--no-sandbox'], }, userDataDir='./userdata',
    #                        args=['--window-size=1500,768'])
    browser = await launch(headless=False, args=(['--no-sandbox']),userDataDir='./userdata')
    page=await browser.newPage()
    print(22222222)
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36')
    await page.goto('https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d99PgJ2K&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F')
    width,height=screen_size()
    await page.setViewport({
        'width':width,
        'height':height
    })
    await page.evaluate(
        '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
    await page.type('#TPL_username_1','14556',{'delay': input_time_random - 50})
    # await asyncio.sleep(10)
    await page.type('#TPL_password_1','12344556',{'delay': input_time_random})
    # await page.click('#J_SubmitStatic')
    # await asyncio.sleep(200)
    # await browser.close()
    await page.waitFor(200)

    # 检测页面是否有滑块。原理是检测页面元素。
    slider = await page.Jeval('#nocaptcha', 'node => node.style')  # 是否有滑块
    if not slider:
        print('没有滑块')
        await page.click('#J_SubmitStatic')
        try:
            global error
            await page.waitFor(200)
            error = await page.Jeval('.error', 'node => node.textContent')# 检测是否是账号密码错误
            print("error_1:", error)
            await page.waitFor(200)
        except Exception as e:
            error = None
            print(e)
        finally:
            if error:
                print('确保账户安全重新入输入')
                # 程序退出。
                await browser.close()
                # asyncio.get_event_loop().run_until_complete(main())
            else:
                print(222222)
                print(page.url)

        # await browser.close()
    else:
        print('有滑块')
        await try_validation(page)
        await page.click('#J_SubmitStatic')
    await asyncio.sleep(200)
async def try_validation(page,distance=508):
    distance1=distance-10
    distance2=10
    time.sleep(10)
    btn_position = await page.evaluate('''
              () =>{
               return {
                x: document.querySelector('#nc_1_n1z').getBoundingClientRect().x,
                y: document.querySelector('#nc_1_n1z').getBoundingClientRect().y,
                width: document.querySelector('#nc_1_n1z').getBoundingClientRect().width,
                height: document.querySelector('#nc_1_n1z').getBoundingClientRect().height
                      }
                    }
                    ''')
    x = btn_position['x'] + btn_position['width'] / 2
    y = btn_position['y'] + btn_position['height'] / 2
    # print(btn_position)
    await page.mouse.move(x, y)
    await page.mouse.down()
    await page.mouse.move(x + distance1, y, {'steps': 30})
    await page.waitFor(800)
    await page.mouse.move(x + distance1 + distance2, y, {'steps': 20})
    await page.waitFor(800)
    await page.mouse.up()
asyncio.get_event_loop().run_until_complete(main())
# 获取登录后cookie
async def get_cookie(page):
    cookies_list = await page.cookies()
    cookies = ''
    for cookie in cookies_list:
        str_cookie = '{0}={1};'
        str_cookie = str_cookie.format(cookie.get('name'), cookie.get('value'))
        cookies += str_cookie
    return cookies


# Response = namedtuple("rs", "title url html cookies headers history status")
#
#
# async def get_html(url, timeout=30):
#     # 默认30s
#     browser = await launch(headless=False, args=['--no-sandbox'])
#     page = await  browser.newPage()
#     res = await page.goto(url, options={'timeout': int(timeout * 1000)})
#     data = await page.content()
#     title = await page.title()
#     resp_cookies = await page.cookies()
#     resp_headers = res.headers
#     resp_history = None
#     resp_status = res.status
#     response = Response(title=title, url=url,
#                         html=data,
#                         cookies=resp_cookies,
#                         headers=resp_headers,
#                         history=resp_history,
#                         status=resp_status)
#     return response
#
#
# if __name__ == '__main__':
#     url_list = ["http://www.10086.cn/index/tj/index_220_220.html", "http://www.10010.com/net5/011/",
#                 "http://python.jobbole.com/87541/"]
#     task = (get_html(url) for url in url_list)
#
#     loop = asyncio.get_event_loop()
#     results = loop.run_until_complete(asyncio.gather(*task))
#     for res in results:
#         print(res.title)