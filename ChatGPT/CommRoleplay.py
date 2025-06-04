import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import openai
import asyncio


# OpenAI Key laden aus der .env Datei
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") 

# Konstruktor für das Rollenspiel-Cog
class Roleplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}  # Um die Sitzungen für die Benutzer zu verfolgen

    # Slash Command für Roleplay
    @slash_command()
    async def roleplay(self, ctx, chatgpt_role: Option(str, "Welche Rolle soll ChatGPT spielen?"), user_role: Option(str, "Welche Rolle spielst du?"), theme: Option(str, "Was ist das Thema des Rollenspiels?")):
        await ctx.defer()

        # Einleitung für das Rollenspiel
        roleplay_intro = f"Dies ist ein Rollenspiel. Ich werde als '{chatgpt_role}' spielen, und du bist '{user_role}'. Unser Thema ist '{theme}'. Los geht's!"
        messages = [
            {"role": "system", "content": f"Du bist {chatgpt_role}. Dies ist ein Rollenspiel basierend auf dem Thema: {theme}."},
            {"role": "user", "content": roleplay_intro}
        ]

        # Sende die Einleitung
        await ctx.followup.send(roleplay_intro)

        # Speichere die Sitzung
        self.sessions[ctx.author.id] = {
            "messages": messages,
            "message_count": 0,
            "timeout_task": None
        }

        # Starte die Timeout-Überwachung
        self.start_timeout(ctx)

    # Timeout überwachen
    async def start_timeout(self, ctx):
        try:
            # Timeout Task für 2 Minuten
            self.sessions[ctx.author.id]['timeout_task'] = asyncio.create_task(self.timeout_check(ctx))
        except KeyError:
            return  # Sitzung bereits beendet

    # Timeout überprüfen
    async def timeout_check(self, ctx):
        await asyncio.sleep(120)  # Warte 2 Minuten
        if ctx.author.id in self.sessions:
            await ctx.followup.send("Das Rollenspiel wurde beendet, da keine Antwort gegeben wurde.")
            del self.sessions[ctx.author.id]

    # Nachrichten verarbeiten
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Wenn der Benutzer eine Antwort im Rollenspiel gibt
        if message.author.id in self.sessions:
            session = self.sessions[message.author.id]
            session['messages'].append({"role": "user", "content": message.content})
            session['message_count'] += 1

            # Überprüfe das Nachrichtenlimit
            if session['message_count'] >= 10:
                await message.channel.send("Das Rollenspiel wurde beendet, da das Nachrichtenlimit erreicht wurde.")
                del self.sessions[message.author.id]
                return

            # Starte die Timeout-Task neu
            if session['timeout_task']:
                session['timeout_task'].cancel()
            await self.start_timeout(message)

            # Frage ChatGPT nach der Antwort
            try:
                result = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # Oder gpt-4
                    messages=session['messages']
                )
                response_text = result['choices'][0]['message']['content']

                # Sende die Antwort
                await message.channel.send(response_text)

                # Füge die Antwort von ChatGPT zu den Nachrichten hinzu
                session['messages'].append({"role": "assistant", "content": response_text})

            except Exception as e:
                await message.channel.send(f"Fehler bei der API-Anfrage: {str(e)}")

# Setup Methode
def setup(bot: discord.Bot):
    bot.add_cog(Roleplay(bot))
