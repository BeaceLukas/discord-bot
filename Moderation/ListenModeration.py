import os
import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.swear_words = self.load_swear_words()

    def load_swear_words(self):
        # Lade Schimpfwörter aus zwei verschiedenen Dateien
        swear_words = set()
        base_dir = os.path.dirname(__file__)
        paths = [
            os.path.join(base_dir, "swear_words_en"),
            os.path.join(base_dir, "swear_word_multilengual"),
        ]
        
        for path in paths:
            try:
                with open(path, "r", encoding="utf-8") as file:
                    # Füge die Schimpfwörter zur Menge hinzu und bereinige Leerzeichen
                    words = {line.strip().lower() for line in file if line.strip()}
                    swear_words.update(words)
                    print(f"Geladene Schimpfwörter von {path}")  # Debug: Zeige geladene Schimpfwörter an
            except FileNotFoundError:
                print(f"Schimpfwörter-Datei nicht gefunden: {path}")

        return swear_words

    async def contains_swear_word(self, message_content):
        # Nachricht in Kleinbuchstaben umwandeln
        message_content = message_content.lower().strip()
        
        # Debug: Überprüfe den Inhalt der Nachricht
        if not message_content:
            print("Nachrichteninhalt ist leer!")  # Prüfen, ob die Nachricht leer ist
            return False

        words_in_message = set(message_content.split())
        print(f"Analysierte Wörter in der Nachricht: {words_in_message}")  # Debug: Zeigt die analysierten Wörter an

        # Prüfe für exakte Wortübereinstimmungen
        for word in words_in_message:
            if word in self.swear_words:
                print(f"Exaktes Schimpfwort gefunden: {word}")  # Debug: Wort gefunden
                return True

        # Prüfe für Übereinstimmungen innerhalb des gesamten Nachrichtentextes
        for swear_word in self.swear_words:
            if swear_word in message_content:
                print(f"Schimpfwort als Substring gefunden: {swear_word}")  # Debug: Substring gefunden
                return True

        print("Kein Schimpfwort in der Nachricht gefunden.")  # Debug: Keine Übereinstimmung gefunden
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        # Prüfe, ob der on_message-Listener aktiv ist
        print("on_message-Listener aktiviert.")  # Debug: Listener-Status
        
        if message.author.bot:
            print("Nachricht von einem Bot, wird ignoriert.")  # Debug: Ignoriert Bots
            return

        # Debug: Zeige den Autor und den Inhalt der Nachricht an
        print(f"Nachricht von {message.author} (ID: {message.author.id}): {message.content}")

        # Prüfe die Nachricht auf Schimpfwörter
        if await self.contains_swear_word(message.content):  # Korrektur: await hinzugefügt
            try:
                # Timeout für 5 Minuten verhängen
                await message.author.timeout_for(timedelta(minutes=5))
                await message.channel.send(f"{message.author.mention} wurde wegen unangemessener Sprache für 5 Minuten stummgeschaltet.")
                print(f"Timeout für {message.author} verhängt.")  # Debug: Timeout erfolgreich
            except discord.Forbidden:
                print("Fehler: Keine Berechtigung für Timeout.")  # Debug: Berechtigungsfehler
            except Exception as e:
                print(f"Fehler beim Timeout: {e}")

# Setup-Methode zum Laden der Moderation-Klasse als Cog
def setup(bot: discord.Bot):
    bot.add_cog(Moderation(bot))
