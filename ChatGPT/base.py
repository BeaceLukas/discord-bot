#.env
import os
from dotenv import load_dotenv      #pip install python-dotenv

#Discord
import discord
from discord.ext import commands
from discord.commands import slash_command, Option

#OpenAI
import openai       #pip install openai



# OpenAI Key laden aus der .env Datei
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # OpenAI API Key
openai.api_key = OPENAI_API_KEY

#Konstrukter
class GPT(commands.Cog):
    def __init__(self, bot):    
        self.bot = bot

    #Test Befehl
    @slash_command()
    async def gpt(self,ctx, text: Option(str)):
        await ctx.defer()
        result = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "system", "content": "Du bist Coding-Assistent"},
                {"role": "user", "content": text}
            ]
        )
        print(result)
    



#Setup Methode
def setup(bot: discord.Bot):
    bot.add_cog(GPT(bot))