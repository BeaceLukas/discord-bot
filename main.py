#.env
import os
from dotenv import load_dotenv      #pip install python-dotenv

#Discord
import discord
from discord.commands import Option


intents = discord.Intents.default()
intents.message_content = True  # Aktiviert das Lesen von Nachrichteninhalten

#Bot Status
status = discord.Status.idle
activity = discord.Activity(type=discord.ActivityType.listening, name="very good music, for sure")


#bot personaliesieren
bot = discord.Bot(          
    intents=intents,        #Zugriff auf ältere Nachrichten
    debug_guilds=[873866388580728852],      #Server zugriffsrechte
    status = status,     #bot staus
    activity = activity     #bot activity
    )

#Start nachricht: ist der Bot on (Yes/No)
@bot.event
async def on_ready():
    print(f"{bot.user} ist Online")     



#Test Befehle

#Test Slash Command, welcher einen User nachdem verwenden begrüßt
@bot.slash_command(desciption="Grüße einen User")
async def greet(ctx, user: Option(discord.Member, "Der User, den du grüßen möchtest")):     
    await ctx.respond(f"Hallo {user.mention} das ist Version 1.6.3")



    #Startet den Bot, mit dem Bot Token aus der .env Datei

#Lädt die einzellnen Dateien in die main
bot.load_extension("ChatGPT.base")
bot.load_extension("ChatGPT.CommRoleplay")
bot.load_extension("ChatGPT.CommSachlich")
bot.load_extension("ChatGPT.CommKritisch")
bot.load_extension("ChatGPT.CommRechtschreibung")
bot.load_extension("ChatGPT.CommCode")

bot.load_extension("Moderation.ListenModeration")

bot.load_extension("GPTChannel.Creat")

#Startet den Discord Bot
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')  # Discord Bot Token
bot.run(DISCORD_TOKEN)