import random
import datetime
import time
import json

import discord
from discord.ext import tasks
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import setup

database_open = open('database.json','r')
database_load = json.load(database_open)

DISCORD_TOKEN = setup.TOKEN
CHROMEDRIVER = "/usr/bin/chromedriver"
URL = "https://p-bandai.jp/chara/c0010/gunpla/"
CHANNEL_ID = database_load['server_info']['channelID']

COMMENT_LIST = database_load['comment_list']

#Setup
#date = datetime.datetime.now()
client = discord.Client(intents = discord.Intents.all())


def save_info(text):

    f = open('info', 'w')
    f.write(text)
    f.close()


def load_info():

    f = open('info', 'r')
    data = f.read()
    f.close()
    return data


@client.event
async def on_ready():

    print('Hello')

    await client.wait_until_ready()
    check_new.start()


@tasks.loop(seconds=60)
async def check_new():

    date = datetime.datetime.now()
    now = datetime.datetime.now().strftime('%H:%M')

    #channel = client.get_channel(CHANNEL_ID)
    #await channel.send('test')

    if now == '09:00':
        
        # setup data
        last_top = load_info()
        is_top = True

        # setup discord channel
        channel = client.get_channel(CHANNEL_ID)
        
        # setup browser options
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--proxy-server="direct://"')
        options.add_argument('--proxy-bypass-list=*')
        options.add_argument('--lang=ja')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36')
        
        # activate the driver
        driver = webdriver.Chrome(CHROMEDRIVER, options=options)
        print('WebDriver successfully activated')

        # try to access the page
        driver.get(URL)
        print('Successfly accessed the page')

        # send comment
        await channel.send(str(date.month)
                           + '月'
                           + str(date.day)
                           + '日の新作・再販情報です！')

        await channel.send(random.choice(COMMENT_LIST))

        # get elements
        article = driver.find_elements(By.CLASS_NAME, 'article_area')
        
        for a in article:

            article_image = a.find_element(By.CLASS_NAME, 'article_photo_s')
            image_url = article_image.find_element(By.TAG_NAME, 'img').get_attribute('src')
            image_title = article_image.find_element(By.TAG_NAME, 'img').get_attribute('alt')

            if is_top == True:

                if image_title == last_top:
                     await channel.send('今日の新着情報はありません')
                     save_info(image_title)
                     break
                else:
                    save_info(image_title)
                    is_top = False

            if is_top == False:

                href = a.find_element(By.TAG_NAME, 'a').get_attribute('href')

                description = a.find_element(By.CLASS_NAME, 'summary')

                price = a.find_element(By.CLASS_NAME, 'price')

                embed = discord.Embed(title = image_title, color = 0x00ff00, description = description.text,  url = href)

                embed.set_image(url=image_url)

                #embed.add_field(name = "追加日", value = str(date.month) + '/' + str(date.day), inline=False)
                embed.add_field(name = "価格", value = price.text)
                await channel.send(embed=embed)

        driver.quit()

client.run(DISCORD_TOKEN)
