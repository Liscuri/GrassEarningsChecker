import discord
from discord.ext import commands, tasks
import json
import asyncio

# Selenium Utils
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# PIL Utils
from PIL import Image

# Other Utils
from io import BytesIO
import time
import schedule
import os
import datetime

# Load configuration
with open("config.json", "r") as f:
    config = json.load(f)

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.remove_command("help")


@bot.event
async def on_ready():
    print('Bot is ready to show your Grass earnings!')
    await bot.change_presence(status=discord.Status.online)
    await bot.change_presence(activity=discord.Game(name="Grass Earnings - by brayden.nl"))
    bot.loop.create_task(screenshot_schedule())


# Function to capture Grass dashboard screenshots
async def capture_grass_dashboard_screenshots(username, password):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://app.getgrass.io/"
        driver.get(url)

        username_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                              'body > div.css-t1k2od > div > div.css-0 > div > div.css-10heyz4 > div > form > div.chakra-stack.css-1f5ypih > div:nth-child(1) > div > input'))
        )
        password_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                              'body > div.css-t1k2od > div > div.css-0 > div > div.css-10heyz4 > div > form > div.chakra-stack.css-1f5ypih > div:nth-child(2) > div > input'))
        )

        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        time.sleep(5)

        WebDriverWait(driver, 30).until(
            EC.url_to_be("https://app.getgrass.io/dashboard")
        )

        span_to_click = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        'body > div.css-872ntn > div.css-315vt6 > main > div.css-1jvqr35 > div.css-17yzblk > div.css-0 > div > label.chakra-switch.css-1lou8h4 > span'))
        )
        span_to_click.click()

        time.sleep(1)

        element1 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                              'body > div.css-872ntn > div.css-315vt6 > main > div.css-0 > div > div.css-corori > div:nth-child(1) > div.chakra-card.css-1p6vixr > div'))
        )
        location1 = element1.location_once_scrolled_into_view
        size1 = element1.size
        screenshot1 = driver.get_screenshot_as_png()
        screenshot1 = Image.open(BytesIO(screenshot1))
        left1 = location1['x']
        top1 = location1['y']
        right1 = left1 + size1['width']
        bottom1 = top1 + size1['height']
        element_screenshot1 = screenshot1.crop((left1, top1, right1, bottom1))
        element_screenshot1.save("screenshot1.png")

        element2 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                              'body > div.css-872ntn > div.css-315vt6 > main > div.css-0 > div > div.css-corori > div.css-1l8nyg0 > div > div'))
        )
        location2 = element2.location_once_scrolled_into_view
        size2 = element2.size
        screenshot2 = driver.get_screenshot_as_png()
        screenshot2 = Image.open(BytesIO(screenshot2))
        left2 = location2['x']
        top2 = location2['y']
        right2 = left2 + size2['width']
        bottom2 = top2 + size2['height']
        element_screenshot2 = screenshot2.crop((left2, top2, right2, bottom2))
        element_screenshot2.save("screenshot2.png")

    finally:
        driver.quit()


async def screenshot_schedule():
    while True:
        print("Scheduled task running...")

        username = config["USERNAME"]
        password = config["PASSWORD"]
        await capture_grass_dashboard_screenshots(username, password)

        channel = bot.get_channel(config["CHANNEL"])
        if channel:
            embed1 = discord.Embed(title="Earnings 🚀", color=0x00ff00)
            embed1.set_image(url="attachment://screenshot1.png")
            embed1.set_footer(text="Grass Earnings Checker Bot - By brayden.nl")

            embed2 = discord.Embed(title="Statistics 📊", color=0x00ff00)
            embed2.set_image(url="attachment://screenshot2.png")
            embed2.set_footer(text="Grass Earnings Checker Bot - By brayden.nl")

            embed3 = discord.Embed(title="Socials 📢", color=0x00ff00)
            embed3.add_field(name="Twitter", value="[Follow me on X](https://x.com/BraydenTweeting)", inline=False)
            embed3.add_field(name="GitHub", value="[Check out my GitHub](https://github.com/Liscuri)", inline=False)
            embed3.add_field(name="Discord", value="[Join my Discord](https://discord.gg/Liscuri)", inline=False)
            embed3.add_field(name="Grass",
                             value="[Check out Grass](https://app.getgrass.io/register/?referralCode=BgxJIZyS1BvmkUq)",
                             inline=False)
            embed3.set_footer(text=f"Time sent: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Send embeds with files attached
            with open('screenshot1.png', 'rb') as f1, open('screenshot2.png', 'rb') as f2:
                file1 = discord.File(f1, filename='screenshot1.png')
                file2 = discord.File(f2, filename='screenshot2.png')
                await channel.send(embed=embed1, file=file1)
                await channel.send(embed=embed2, file=file2)
                await channel.send(embed=embed3)
                f1.close()
                f2.close()
                os.remove('screenshot1.png')
                os.remove('screenshot2.png')
        await asyncio.sleep(300)


bot.run(config["TOKEN"])
