import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import openai

# Lade Umgebungsvariablen aus der .env Datei
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Konstruktor für Comm-Kritisch
class Kritisch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Kritischer Befehl (Slash Command)
    @slash_command()
    async def kritisch(self, ctx, thema: Option(str, "Welches Thema soll kritisch hinterfragt werden?")):
        await ctx.defer()  # Verzögerung, falls die Antwort lange dauert

        # Erstelle die Anfrage an ChatGPT
        try:
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Du kannst hier auch gpt-4 verwenden
                messages=[
                    {"role": "system", "content": "Du bist ein kritischer Denker. Stelle das gegebene Thema in Frage und analysiere die Vor- und Nachteile."},
                    {"role": "user", "content": f"Untersuche das Thema '{thema}' kritisch. Stelle es in Frage: Ist es effektiv oder unnötig? Zeige Vor- und Nachteile auf und begründe."}
                ]
            )

            # Extrahiere die Antwort von ChatGPT
            antwort = result['choices'][0]['message']['content']

            # Sende die Antwort im Discord-Kanal
            await ctx.followup.send(antwort)

        except Exception as e:
            # Fehlerbehandlung, falls etwas schiefgeht
            await ctx.followup.send(f"Fehler bei der Anfrage: {str(e)}")

# Setup Methode
def setup(bot: discord.Bot):
    bot.add_cog(Kritisch(bot))
