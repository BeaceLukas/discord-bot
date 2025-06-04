import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from discord import ButtonStyle, Embed, Interaction, ui
import asyncio
import openai

# Lade Umgebungsvariablen aus der .env Datei
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Konstruktor für den Chat-Cog
class NeuerChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_channels = {}  # Speichert aktive Channels

    # Befehl zum Erstellen eines neuen Chats (Slash Command)
    @slash_command()
    async def neuen_chat(self, ctx):
        print(f"{ctx.author.name} hat /neuen_chat verwendet.")
        user_channels = [ch for ch in ctx.guild.text_channels if ch.name.startswith(f"privat-chat-{ctx.author.name}")]

        # Überprüfe, ob der Benutzer die maximale Anzahl von 2 Channels erreicht hat
        if len(user_channels) >= 2:
            oldest_channel = user_channels[0]  # Ältesten Channel bestimmen
            confirm_view = ui.View()  # Bestätigungsansicht erstellen

            # Erstelle Bestätigungs- und Abbrechen-Buttons
            confirm_button = ui.Button(label="Bestätigen", style=ButtonStyle.danger)
            cancel_button = ui.Button(label="Abbrechen", style=ButtonStyle.secondary)

            # Callback für die Bestätigung des Löschens
            async def confirm_callback(interaction):
                await oldest_channel.delete()  # Lösche den ältesten Channel
                await self.create_channel(ctx)  # Erstelle einen neuen Channel
                await interaction.response.edit_message(content="Ältester Channel gelöscht und neuer erstellt.", view=None)

            # Callback für das Abbrechen der Aktion
            async def cancel_callback(interaction):
                await interaction.response.edit_message(content="Aktion abgebrochen.", view=None)

            confirm_button.callback = confirm_callback
            cancel_button.callback = cancel_callback

            confirm_view.add_item(confirm_button)
            confirm_view.add_item(cancel_button)

            # Sende die Bestätigungsnachricht
            await ctx.respond(
                f"Du hast bereits die maximale Anzahl von 5 Channels erreicht. "
                f"Möchtest du den ältesten Channel ({oldest_channel.mention}) löschen, um einen neuen zu erstellen?",
                view=confirm_view
            )
        else:
            await self.create_channel(ctx)  # Erstelle einen neuen Channel

    # Hilfsmethode zum Erstellen eines Channels
    async def create_channel(self, ctx):
        guild = ctx.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel_name = f"privat-chat-{ctx.author.name}"  # Erstelle den Channel-Namen
        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        self.active_channels[ctx.author.id] = channel.id  # Speichere den Channel

        print(f"Channel {channel.name} für {ctx.author.name} erstellt.")
        await ctx.respond(f"Channel {channel.mention} wird erstellt...")
        await asyncio.sleep(3)  # Kurze Pause, um die Erstellung zu simulieren
        
        # Sende eine Begrüßungsnachricht im neuen Channel
        await channel.send(content=ctx.author.mention)
        embed = Embed(title="Wilkommen in deinem neuen Chat!!", description="Wähle deinen gewünschten Sprach-modus, um mit Chat-GPT einen Längeren Chat zu führen. Um den Chat zu beenden nutze den Befehl /exit.       /rename zum umbenenen; /invite um User dem Channel hinzuzufügen; /remove um User zu entfernen;", color=discord.Color.blue())
        view = self.StartModusListener(self.bot, self)  # Instanziere die Listener-Ansicht

        await channel.send(embed=embed, view=view)
        await ctx.send_followup(f"Neuer Channel {channel.mention} erstellt.")

    # Befehl zum Umbenennen des Channels
    @slash_command()
    async def rename(self, ctx, neuer_name: Option(str, "Neuer Name für den Channel")):
        print(f"{ctx.author.name} hat /rename verwendet mit dem neuen Namen: {neuer_name}.")
        if ctx.channel.id == self.active_channels.get(ctx.author.id):
            await ctx.channel.edit(name=neuer_name)  # Benenne den Channel um
            await ctx.respond(f"Channel-Name wurde zu **{neuer_name}** geändert.")
        else:
            await ctx.respond("Dieser Befehl kann nur in deinem erstellten Channel verwendet werden.", ephemeral=True)

    # Befehl zum Verlassen des Channels
    @slash_command()
    async def exit(self, ctx):
        print(f"{ctx.author.name} hat /exit verwendet.")
        if ctx.channel.id == self.active_channels.get(ctx.author.id):
            confirm_view = ui.View()  # Bestätigungsansicht für das Löschen

            confirm_button = ui.Button(label="Bestätigen", style=ButtonStyle.danger)
            cancel_button = ui.Button(label="Abbrechen", style=ButtonStyle.secondary)

            async def confirm_callback(interaction):
                await interaction.response.send_message("Channel wird gelöscht...", ephemeral=True)
                await ctx.channel.delete()  # Lösche den Channel
                self.active_channels.pop(ctx.author.id, None)  # Entferne den Channel aus der Liste

            async def cancel_callback(interaction):
                await interaction.response.send_message(content="Aktion abgebrochen.", ephemeral=True)

            confirm_button.callback = confirm_callback
            cancel_button.callback = cancel_callback

            confirm_view.add_item(confirm_button)
            confirm_view.add_item(cancel_button)

            await ctx.respond("Möchtest du diesen Channel wirklich löschen?", view=confirm_view)
        else:
            await ctx.respond("Dieser Befehl kann nur in deinem erstellten Channel verwendet werden.", ephemeral=True)

    # Befehl zum Einladen eines Benutzers
    @slash_command()
    async def invite(self, ctx, user: Option(discord.Member, "Wähle den Benutzer, der eingeladen werden soll")):
        print(f"{ctx.author.name} hat /invite verwendet, um {user.name} einzuladen.")
        if ctx.channel.id == self.active_channels.get(ctx.author.id):
            await ctx.channel.set_permissions(user, read_messages=True, send_messages=True)  # Setze Berechtigungen für den Benutzer
            await ctx.respond(f"{user.mention} wurde zum Channel eingeladen.")
        else:
            await ctx.respond("Dieser Befehl kann nur in deinem erstellten Channel verwendet werden.", ephemeral=True)

    # Befehl zum Entfernen eines Benutzers
    @slash_command()
    async def remove(self, ctx, user: Option(discord.Member, "Wähle den Benutzer, der entfernt werden soll")):
        print(f"{ctx.author.name} hat /remove verwendet, um {user.name} zu entfernen.")
        if ctx.channel.id == self.active_channels.get(ctx.author.id):
            if user == self.bot.user or user == ctx.author:
                await ctx.respond("Du kannst dich selbst oder den Bot nicht entfernen.", ephemeral=True)
            else:
                await ctx.channel.set_permissions(user, overwrite=None)  # Entferne die Berechtigungen des Benutzers
                await ctx.respond(f"{user.mention} wurde aus dem Channel entfernt.")
        else:
            await ctx.respond("Dieser Befehl kann nur in deinem erstellten Channel verwendet werden.", ephemeral=True)

    # Listener für Modus-Auswahl
    class StartModusListener(ui.View):
        def __init__(self, bot, cog):
            super().__init__()
            self.bot = bot
            self.cog = cog
            self.add_item(ui.Button(label="Sachlich", style=ButtonStyle.primary, custom_id="start_sachliche"))
            self.add_item(ui.Button(label="Code", style=ButtonStyle.secondary, custom_id="start_code"))
            self.add_item(ui.Button(label="Kritisch", style=ButtonStyle.success, custom_id="start_kritisch"))

        # Überprüfe die Interaktion des Benutzers
        async def interaction_check(self, interaction: Interaction):
            if interaction.custom_id in ["start_sachliche", "start_code", "start_kritisch"]:
                channel = interaction.channel
                mode_messages = {
                    "start_sachliche": "Du bist ein sachlicher Assistent.",
                    "start_code": "Du bist ein Programmierassistent.",
                    "start_kritisch": "Du hinterfragst und kritisierst effektiv."
                }
                self.cog.active_channels[channel.id] = {
                    "mode": interaction.custom_id,
                    "messages": [{"role": "system", "content": mode_messages[interaction.custom_id]}]
                }
                mode_names = {
                    "start_sachliche": "Sachlich",
                    "start_code": "Code",
                    "start_kritisch": "Kritisch"
                }
                await interaction.response.send_message(
                    f"{mode_names[interaction.custom_id]}-Modus aktiviert. Ich werde auf alle Nachrichten in diesem Modus antworten."
                )
                await channel.send(f"Der {mode_names[interaction.custom_id]}-Modus ist jetzt aktiv. Schreibe eine Nachricht, und ich antworte darauf.")
                return True
            return False

    # Listener für Nachrichten im Channel
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.active_channels and not message.author.bot:
            context = self.active_channels[message.channel.id]["messages"]
            user_message = {"role": "user", "content": message.content}
            context.append(user_message)  # Füge die Benutzer-Nachricht hinzu
            try:
                result = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # Du kannst hier auch gpt-4 verwenden
                    messages=context  # Nutze den Nachrichtenkontext für die Antwort
                )
                bot_message = result['choices'][0]['message']['content']
                await message.channel.send(bot_message)  # Sende die Antwort des Bots
                context.append({"role": "assistant", "content": bot_message})  # Füge die Bot-Antwort zum Kontext hinzu
            except Exception as e:
                await message.channel.send(f"Fehler bei der Anfrage: {str(e)}")

# Setup Methode
def setup(bot: discord.Bot):
    bot.add_cog(NeuerChat(bot))
