import discord
from .services import UIDService
from discord import app_commands
from discord.ext import commands
from typing import Optional

class UIDBot:
    """
    Discord bot for managing whitelisted UIDs.
    """

    def __init__(self, token: str, guild_id: Optional[int] = None):
        self.token = token
        self.guild_id = guild_id
        self.uids = UIDService()

        self.intents = discord.Intents.all()
        self.bot = commands.Bot(command_prefix="/", intents=self.intents)

        self._register_events()
        self._register_commands()

    # ------------------ HELPERS ------------------ #
    @staticmethod
    def embed_message(title: str, description: str, color: int = 0x00FF00):
        return discord.Embed(title=title, description=description, color=color)

    @staticmethod
    def format_uid_list(uids_list):
        if not uids_list:
            return "Whitelist is empty."
        return "\n".join(f"- {uid}" for uid in uids_list)

    # ------------------ EVENTS ------------------ #
    def _register_events(self):
        @self.bot.event
        async def on_ready():
            print(f"[BOT] Logged in as {self.bot.user}")
            # Guild-based sync for instant slash command availability
            if self.guild_id:
                guild = discord.Object(id=self.guild_id)
                self.bot.tree.copy_global_to(guild=guild)
                await self.bot.tree.sync(guild=guild)
                print(f"[BOT] Commands synced to guild {self.guild_id}")
            else:
                await self.bot.tree.sync()
                print("[BOT] Commands synced globally")

    # ------------------ SLASH COMMANDS ------------------ #
    def _register_commands(self):
        @self.bot.tree.command(name="checkuid", description="Check if a UID exists in whitelist")
        @app_commands.describe(uid="UID to check")
        async def checkuid(interaction: discord.Interaction, uid: str):
            exists = self.uids.uid_exists(uid)
            color = 0x00FF00 if exists else 0xFF0000
            description = f"✅ UID `{uid}` exists." if exists else f"❌ UID `{uid}` does not exist."
            await interaction.response.send_message(embed=self.embed_message("Check UID", description, color))

        @self.bot.tree.command(name="adduid", description="Add a UID to whitelist")
        @app_commands.describe(uid="UID to add")
        async def adduid(interaction: discord.Interaction, uid: str):
            added = self.uids.add_uid(uid)
            color = 0x00FF00 if added else 0xFFFF00
            description = f"✅ UID `{uid}` added." if added else f"⚠️ UID `{uid}` already exists."
            await interaction.response.send_message(embed=self.embed_message("Add UID", description, color))

        @self.bot.tree.command(name="removeuid", description="Remove a UID from whitelist")
        @app_commands.describe(uid="UID to remove")
        async def removeuid(interaction: discord.Interaction, uid: str):
            removed = self.uids.remove_uid(uid)
            color = 0x00FF00 if removed else 0xFFFF00
            description = f"✅ UID `{uid}` removed." if removed else f"⚠️ UID `{uid}` not found."
            await interaction.response.send_message(embed=self.embed_message("Remove UID", description, color))

        @self.bot.tree.command(name="listuids", description="List all whitelisted UIDs")
        async def listuids(interaction: discord.Interaction):
            all_uids = self.uids.get_all_uids()
            description = self.format_uid_list(all_uids)
            await interaction.response.send_message(embed=self.embed_message("Whitelist UIDs", description, 0x0099FF))

    # ------------------ RUN BOT ------------------ #
    def run(self):
        if not self.token:
            print("[BOT] Token not provided. Skipping bot startup.")
            return
        self.bot.run(self.token)