import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import openai

# Lade Umgebungsvariablen aus der .env Datei
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Konstruktor für Comm-Code
class Code(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Code Befehl (Slash Command)
    @slash_command()
    async def code(
        self,
        ctx,
        aufgabe: Option(str, "Beschreibe die Programmieraufgabe."),
        sprache: Option(str, "Wähle die Programmiersprache:", choices=["Python", "Java", "C"]),
        code: Option(str, "Optional: Füge bestehenden Code hinzu.", required=False)
    ):
        await ctx.defer()  # Verzögerung, falls die Antwort lange dauert

        # Erstelle die Anfrage an ChatGPT
        try:
            # Zusammenstellung der Anfrage
            nachricht = f"Ich habe die folgende Programmieraufgabe: '{aufgabe}'. " \
                        f"Die gewählte Programmiersprache ist {sprache}. "
            if code:
                nachricht += f"Der bestehende Code lautet: '{code}'. "
            nachricht += "Bitte löse die Aufgabe."

            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Du kannst hier auch gpt-4 verwenden
                messages=[
                    {"role": "system", "content": "Du bist ein Programmierassistent."},
                    {"role": "user", "content": nachricht}
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
    bot.add_cog(Code(bot))
