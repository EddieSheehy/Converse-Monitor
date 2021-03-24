import requests
from bs4 import BeautifulSoup as bs
import time
import discord
from discord_webhook import *
from threading import Thread
from proxycrawl import CrawlingAPI, ScraperAPI, LeadsAPI

TOKEN = 'NzExMjU2NjU4NTkyMTM3MjM3.XsAXYQ.RsuGF9pIAtU3dguVz7-EclQRy34'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.30 Safari/537.36'}
client = discord.Client()
webhookurl = 'https://discord.com/api/webhooks/824026633555673148/QO-MQQckOkJyIcCIL9OjLIt0BrZPXdAxEzEWo03-4VpGHeemYRvyE5mUp9qolTTOwCVl'
delay = 6
instock = 0
productfound = 0
sizefindretries = 0
checksizes = []
##########################################################################

s = requests.Session()

def ConverseMonitor(productfound,sizefindretries):
    query = "chuck"
    query2 = ""

    while 1:

        url = 'https://www.converse.com/on/demandware.store/Sites-converse-eu-Site/en_IE/Search-Show?q=high'
        result = requests.get(url,headers=headers).text
        soup = bs(result, 'lxml')
        
        john = soup.find_all('div', class_='product-tile')

        for image in john:
            product_link = image.find('div', attrs={'class':'product-image'}).a.get('href')
            product_image = image.find('div', attrs={'class':'product-image'}).a.img.get('src')
            product_title = image.find('div', attrs={'class':'product-image'}).a.get('title')
            product_price = image.find('div', attrs={'class':'product-pricing'}).span.text
            if(query.lower() in product_title.lower() and query2.lower() in product_title.lower()): # If the keywords match a products title.
                ##############################################                  # Discord Webhook for 'Found Product'
                if(productfound == 0):
                    webhook = DiscordWebhook(url=webhookurl, username="Converse", avatar_url='https://1000logos.net/wp-content/uploads/2019/06/Converse-Logo-2007.jpg') 
                    embed = DiscordEmbed(title = product_title, url = product_link, colour = 3066993)
                    embed.add_embed_field(name='Site', value='Converse', inline=True)
                    embed.add_embed_field(name='Product Name', value=product_title, inline=False)
                    embed.add_embed_field(name='Price', value=product_price, inline=True)
                    embed.add_embed_field(name='Product Loaded', value='Product Loaded', inline=True)
                    embed.set_footer(text='Watson - Keywords = '+query+','+query2,icon_url='https://cdn.discordapp.com/app-icons/711256658592137237/74a1779046799c1665d03cda5bb9694f.png'),
                    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/824026618019184711/824054318398308372/image0.jpg')
                    embed.set_timestamp()
                    webhook.add_embed(embed)
                    webhook.execute()
                    print('Converse: Product Found & Webhook Executed -  '+product_title)
                    getsizes(product_link, product_image, product_title, product_price,query,query2, instock, sizefindretries)

                if(productfound == 1):
                    getsizes(product_link, product_image, product_title, product_price,query,query2, instock, sizefindretries)

            else:
                print('Nope')

def getsizes(product_link, product_image, product_title, product_price, query, query2, instock, sizefindretries):

    i = 0
    sizes = [] * 100
    
    url = product_link
    result = requests.get(url,headers=headers).text
    soup = bs(result, 'lxml')

    product = soup.find('select', attrs={'id':'variationDropdown-size'})

    for value in product.stripped_strings:
        sizes.append(value)
        i = i +1
    sizes[0] = ''
    makeitastring = ' '.join(map(str, sizes))
    newsizes = makeitastring.replace(' ','\n')
    checksizes = sizes
    ##############################################              # Discord Webhook for 'Getting Sizes'
    if(len(sizes) > 1 and instock == 0):
        webhook = DiscordWebhook(url=webhookurl, username="Converse", avatar_url='https://1000logos.net/wp-content/uploads/2019/06/Converse-Logo-2007.jpg') 
        embed = DiscordEmbed(title = product_title, url = product_link, colour = 3066993)
        embed.add_embed_field(name='Site', value='Converse', inline=True)
        embed.add_embed_field(name='Product Name', value=product_title, inline=False)
        embed.add_embed_field(name='Price', value=product_price, inline=False)
        embed.add_embed_field(name='Sizes', value=newsizes, inline=True)  
        embed.set_footer(text='Watson - Keywords = '+query+','+query2,icon_url='https://cdn.discordapp.com/app-icons/711256658592137237/74a1779046799c1665d03cda5bb9694f.png'),
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/824026618019184711/824054318398308372/image0.jpg')
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()
        print('Converse: Sizes Found & Webhook Executed -  '+product_title)
        instock = 1
        
        getsizes(product_link, product_image, product_title, product_price,query,query2, instock,sizefindretries)

    ##############################################

    if(sizes != checksizes):
        instock = 0
        if len(sizes) == 1:
            print('Sizes OOS')
            time.sleep(5)
            getsizes(product_link, product_image, product_title, product_price,query,query2, instock,sizefindretries)
        else:
            getsizes(product_link, product_image, product_title, product_price,query,query2, instock,sizefindretries)

    if(sizes == checksizes):
        print("Waiting For Sizes To Go OOS - ", sizes)
        time.sleep(5)
        getsizes(product_link, product_image, product_title, product_price,query,query2, instock,sizefindretries)
        

        
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Capitalism Is King'))
    thread1 = Thread(target=ConverseMonitor(productfound,sizefindretries))
    thread1.start()

client.run(TOKEN)
