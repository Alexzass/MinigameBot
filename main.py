from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
import requests
import httpx
import random

load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = os.getenv("API_URL")

bot = commands.Bot(command_prefix='?', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
    
@bot.command()
async def play(ctx, type = "single"):
    player_id = ctx.author.id
    server_id = ctx.guild.id
    
    gamemodes = ["Champs", "Items"]
    champ_criteria = ["Name"]
    item_criteria = ["Name", "Cost"]
    gamemode = None
    criteria = None
    player = None
    health = 3
    score = 0
    streak = 0
    highscore = 0
    
    async with httpx.AsyncClient() as client:
        
        ver_res = await client.get(f"https://ddragon.leagueoflegends.com/api/versions.json")
        version = ver_res.json()[0]
        
        print(f"Player ID: {player_id}")
        res = await client.get(f"{API_URL}/player/{player_id}")
    
        if res.json():
            player = res.json()
        else:
            await client.post(f"http://localhost:3000/player/create", json={"user_id": player_id, "state": "online", "server_id": server_id})
            res = await client.get(f"http://localhost:3000/player/{player_id}")
            player = res.json()
        
        if type == "single":
            
            while not gamemode or not criteria:
                if not gamemode:
                    def check(message):
                        return message.author == ctx.author and message.content.lower() in [opt.lower() for opt in gamemodes]
                    try:
                        embed = discord.Embed(
                            title="Choose what to guess", 
                            description="Type one of the options below:", 
                            color=discord.Color.blue()
                        )
                        for option in gamemodes:
                            embed.add_field(name=option, value=f"Type `{option.lower()}` to select this action.", inline=False)
                        
                        await ctx.send(embed=embed)
                        msg = await bot.wait_for("message", check=check, timeout=30)
                        gamemode = msg.content.lower()
                            
                        
                    except TimeoutError:
                        await ctx.send("Got drowsy💤💤💤. Ending the game....")
                        break
                else:
                    if gamemode == "items":
                        def check(message):
                            return message.author == ctx.author and message.content.lower() in [opt.lower() for opt in item_criteria]
                        try:
                            embed = discord.Embed(
                                title="Choose the guess criteria", 
                                description="Type one of the options below:", 
                                color=discord.Color.blue()
                            )
                            for option in item_criteria:
                                embed.add_field(name=option, value=f"Type `{option.lower()}` to select this option.", inline=False)
                            
                            await ctx.send(embed=embed)
                            msg = await bot.wait_for("message", check=check, timeout=30)
                            criteria = msg.content.lower()
                            
                        except TimeoutError:
                            await ctx.send("Got drowsy💤💤💤. Ending the game....")
                            break
                    elif gamemode == "champions":
                        def check(message):
                            return message.author == ctx.author and message.content.lower() in [opt.lower() for opt in champ_criteria]
                        try:
                            embed = discord.Embed(
                                title="Choose the guess criteria", 
                                description="Type one of the options below:", 
                                color=discord.Color.blue()
                            )
                            for option in champ_criteria:
                                embed.add_field(name=option, value=f"Type `{option.lower()}` to select this option.", inline=False)
                            
                            await ctx.send(embed=embed)
                            msg = await bot.wait_for("message", check=check, timeout=30)
                            criteria = msg.content.lower()
                            
                        except TimeoutError:
                            await ctx.send("Got drowsy💤💤💤. Ending the game....")
                            break
                        
            print("Gamemode: ", gamemode)
            print("Criteria: ", criteria)
                        
            if gamemode == "items":
                items = {}
                
                if criteria == "name":
                    highscore = player["highscore_items_name"]
                    res = await client.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json")
                    res = res.json()
                    
                    for k,v in res["data"].items():
                        if v["maps"]["11"] and v["gold"]["purchasable"]:
                            items[k] = v["name"]
                            
                    embed = discord.Embed(
                                title=f"{ctx.author.display_name}'s game", 
                                description=f"Guess the {gamemode} {criteria}", 
                                color=discord.Color(random.randint(0, 0xFFFFFF))
                            )
                    item = random.choice(list(items.keys()))
                    embed.add_field(name="Health", value="🧡 "*health, inline=True)
                    embed.add_field(name="Score", value=score, inline=True)
                    embed.add_field(name="Streak", value="🔥 "*streak, inline=True)
                    embed.add_field(name="Highscore", value=highscore, inline=True)
                    embed.set_thumbnail(url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item}.png")
                    await ctx.send(embed=embed)
                    
                    while health > 0:
                        msg = await bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=30)
                        
                        if msg.content.lower() == items[item].lower() and streak == 2 and health < 3:
                            health += 1
                            streak = 0
                            items.pop(item)
                            item = random.choice(list(items.keys()))
                            embed.set_field_at(index=0,name="Health", value="🧡 "*health, inline=True)
                            embed.set_field_at(index=1,name="Score", value=score, inline=True)
                            embed.set_field_at(index=2,name="Streak", value="🔥 "*streak, inline=True)
                            embed.set_thumbnail(url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item}.png")
                            await ctx.send(embed=embed)
                        elif msg.content.lower() == items[item].lower():
                            score += 1
                            streak += 1
                            items.pop(item)
                            item = random.choice(list(items.keys()))
                            embed.set_field_at(index=1,name="Score", value=score, inline=True)
                            embed.set_field_at(index=2,name="Streak", value="🔥 "*streak, inline=True)
                            embed.set_thumbnail(url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item}.png")
                            await ctx.send(embed=embed)
                        else:
                            if health == 1:
                                break
                            health -= 1
                            streak = 0
                            items.pop(item)
                            item = random.choice(list(items.keys()))
                            embed.set_field_at(index=0,name="Health", value="🧡 "*health, inline=True)
                            embed.set_field_at(index=1,name="Score", value=score, inline=True)
                            embed.set_field_at(index=2,name="Streak", value="🔥 "*streak, inline=True)
                            embed.set_thumbnail(url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item}.png")
                            await ctx.send(embed=embed)
                    if score > highscore:
                        await client.patch(f"http://localhost:3000/player/update/{player_id}", json={"state": "offline", "highscore": score, "highscore_type": "items_name"})
                        await ctx.send(f"New highscore 🆙: {score}")
                    else:
                        await client.patch(f"http://localhost:3000/player/update/{player_id}", json={"state": "offline"})
                        await ctx.send(f"Game ended.")
                        
                    
                    
                    
                    
                elif criteria == "cost":
                    highscore = player["highscore_items_cost"]
                    res = await client.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json")
                    res = res.json()
                    
                    for k,v in res["data"].items():
                        if v["maps"]["11"] and v["gold"]["purchasable"]:
                            items[k] = v["gold"]["total"]
                            
                    embed = discord.Embed(
                                title=f"{ctx.author.display_name}'s game", 
                                description=f"Guess the {gamemode} {criteria}", 
                                color=discord.Color(random.randint(0, 0xFFFFFF))
                            )
                    item = random.choice(list(items.keys()))
                    embed.add_field(name="Health", value="🧡 "*health, inline=True)
                    embed.add_field(name="Score", value=score, inline=True)
                    embed.add_field(name="Streak", value="🔥 "*streak, inline=True)
                    embed.add_field(name="Highscore", value=highscore, inline=True)
                    embed.set_thumbnail(url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item}.png")
                    await ctx.send(embed=embed)
                    
                    while health > 0:
                        msg = await bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=30)
                        
                        if msg.content == str(items[item]) and streak == 2 and health < 3:
                            health += 1
                            streak = 0
                            items.pop(item)
                            item = random.choice(list(items.keys()))
                            embed.set_field_at(index=0,name="Health", value="🧡 "*health, inline=True)
                            embed.set_field_at(index=1,name="Score", value=score, inline=True)
                            embed.set_field_at(index=2,name="Streak", value="🔥 "*streak, inline=True)
                            embed.set_thumbnail(url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item}.png")
                            await ctx.send(embed=embed)
                        elif msg.content == str(items[item]):
                            score += 1
                            streak += 1
                            items.pop(item)
                            item = random.choice(list(items.keys()))
                            embed.set_field_at(index=1,name="Score", value=score, inline=True)
                            embed.set_field_at(index=2,name="Streak", value="🔥 "*streak, inline=True)
                            embed.set_thumbnail(url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item}.png")
                            await ctx.send(embed=embed)
                        else:
                            if health == 1:
                                break
                            health -= 1
                            streak = 0
                            items.pop(item)
                            item = random.choice(list(items.keys()))
                            embed.set_field_at(index=0,name="Health", value="🧡 "*health, inline=True)
                            embed.set_field_at(index=1,name="Score", value=score, inline=True)
                            embed.set_field_at(index=2,name="Streak", value="🔥 "*streak, inline=True)
                            embed.set_thumbnail(url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item}.png")
                            await ctx.send(embed=embed)
                    if score > highscore:
                        await client.patch(f"http://localhost:3000/player/update/{player_id}", json={"state": "offline", "highscore": score, "highscore_type": "items_cost"})
                        await ctx.send(f"New highscore 🆙: {score}")
                    else:
                        await client.patch(f"http://localhost:3000/player/update/{player_id}", json={"state": "offline"})
                        await ctx.send(f"Game ended.")

            elif gamemode == "champs":
                champs = {}
                
                if criteria == "name":
                    highscore = player["highscore_champs_name"]
                    res = await client.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json")
                    res = res.json()
                    
                    for k,v in res["data"].items():
                        champs[k] = v["name"]
                            
                    embed = discord.Embed(
                                title=f"{ctx.author.display_name}'s game", 
                                description=f"Guess the {gamemode} {criteria}", 
                                color=discord.Color(random.randint(0, 0xFFFFFF))
                            )
                    champ = random.choice(list(champs.keys()))
                    embed.add_field(name="Health", value="🧡 "*health, inline=True)
                    embed.add_field(name="Score", value=score, inline=True)
                    embed.add_field(name="Streak", value="🔥 "*streak, inline=True)
                    embed.add_field(name="Highscore", value=highscore, inline=True)
                    embed.set_image(url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_0.jpg")
                    await ctx.send(embed=embed)
                    print(champ)
                    
                    while health > 0:
                        msg = await bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=30)
                        
                        if msg.content.lower() == champs[champ].lower() and streak == 2 and health < 3:
                            health += 1
                            streak = 0
                            champs.pop(champ)
                            champ = random.choice(list(champs.keys()))
                            embed.set_field_at(index=0,name="Health", value="🧡 "*health, inline=True)
                            embed.set_field_at(index=1,name="Score", value=score, inline=True)
                            embed.set_field_at(index=2,name="Streak", value="🔥 "*streak, inline=True)
                            embed.set_image(url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_0.jpg")
                            await ctx.send(embed=embed)
                        elif msg.content.lower() == champs[champ].lower():
                            score += 1
                            if streak == 3:
                                pass
                            else:
                                streak += 1
                            champs.pop(champ)
                            champ = random.choice(list(champs.keys()))
                            embed.set_field_at(index=1,name="Score", value=score, inline=True)
                            embed.set_field_at(index=2,name="Streak", value="🔥 "*streak, inline=True)
                            embed.set_image(url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_0.jpg")
                            await ctx.send(embed=embed)
                        elif msg.content.startswith("?"):
                            await ctx.send("End the current game before using commands.")
                        else:
                            if health == 1:
                                break
                            health -= 1
                            streak = 0
                            champs.pop(champ)
                            champ = random.choice(list(champs.keys()))
                            embed.set_field_at(index=0,name="Health", value="🧡 "*health, inline=True)
                            embed.set_field_at(index=1,name="Score", value=score, inline=True)
                            embed.set_field_at(index=2,name="Streak", value="🔥 "*streak, inline=True)
                            embed.set_image(url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_0.jpg")
                            await ctx.send(embed=embed)
                    if score > highscore:
                        await client.patch(f"http://localhost:3000/player/update/{player_id}", json={"state": "offline", "highscore": score, "highscore_type": "champs_name"})
                        await ctx.send(f"New highscore 🆙: {score}")
                    else:
                        await client.patch(f"http://localhost:3000/player/update/{player_id}", json={"state": "offline"})
                        await ctx.send(f"Game ended.")
                        

@bot.command()
async def lb(ctx):
    gamemodes = ["Champs", "Items"]
    champ_criteria = ["Name"]
    item_criteria = ["Name", "Cost"]
    gamemode = None
    criteria = None
    
    async with httpx.AsyncClient() as client:
            
        while not gamemode or not criteria:
            if not gamemode:
                def check(message):
                    return message.author == ctx.author and message.content.lower() in [opt.lower() for opt in gamemodes]
                try:
                    embed = discord.Embed(
                        title="Choose what to guess", 
                        description="Type one of the options below:", 
                        color=discord.Color.blue()
                    )
                    for option in gamemodes:
                        embed.add_field(name=option, value=f"Type `{option.lower()}` to select this action.", inline=False)
                        
                    await ctx.send(embed=embed)
                    msg = await bot.wait_for("message", check=check, timeout=30)
                    gamemode = msg.content.lower()
                            
                        
                except TimeoutError:
                    await ctx.send("Got drowsy💤💤💤. Ending the game....")
                    break
            else:
                if gamemode == "items":
                    def check(message):
                        return message.author == ctx.author and message.content.lower() in [opt.lower() for opt in item_criteria]
                    try:
                        embed = discord.Embed(
                            title="Choose the guess criteria", 
                            description="Type one of the options below:", 
                            color=discord.Color.blue()
                        )
                        for option in item_criteria:
                            embed.add_field(name=option, value=f"Type `{option.lower()}` to select this option.", inline=False)
                            
                        await ctx.send(embed=embed)
                        msg = await bot.wait_for("message", check=check, timeout=30)
                        criteria = msg.content.lower()
                            
                    except TimeoutError:
                        await ctx.send("Got drowsy💤💤💤. Ending the game....")
                        break
                elif gamemode == "champs":
                    def check(message):
                        return message.author == ctx.author and message.content.lower() in [opt.lower() for opt in champ_criteria]
                    try:
                        embed = discord.Embed(
                            title="Choose the guess criteria", 
                            description="Type one of the options below:", 
                            color=discord.Color.blue()
                        )
                        for option in champ_criteria:
                            embed.add_field(name=option, value=f"Type `{option.lower()}` to select this option.", inline=False)
                            
                        await ctx.send(embed=embed)
                        msg = await bot.wait_for("message", check=check, timeout=30)
                        criteria = msg.content.lower()
                            
                    except TimeoutError:
                        await ctx.send("Got drowsy💤💤💤. Ending the game....")
                        break
                        
        print("Gamemode: ", gamemode)
        print("Criteria: ", criteria)
            
        res = await client.get(f"{API_URL}/leaderboard", params={"highscore_type": f"{gamemode.lower()}_{criteria.lower()}", "limit": 10, "offset": 0})
        
        if res.json():
            embed = discord.Embed(
                title="Leaderboard 🏆", 
                description=f"Top 10 players in {gamemode} by {criteria}", 
                color=discord.Color.gold()
            )
            for i, player in enumerate(res.json()):
                user = await bot.fetch_user(player["user_id"])
                embed.add_field(name=f"{i+1}. {user}", value=f"Score: {player[f'highscore_{gamemode.lower()}_{criteria.lower()}']}", inline=True)
            await ctx.send(embed=embed)
                    
                    
bot.run(DISCORD_BOT_TOKEN)