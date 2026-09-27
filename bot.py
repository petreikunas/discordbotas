import asyncio
import json
import os
import random
import re
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands


# =========================================================
# NUSTATYMAI
# =========================================================

# ĮKLIJUOK NAUJĄ TOKENĄ ČIA
TOKEN = "MTU1MzQ0MjAyMDMyMjgzNjUzMA.GkyXU7.zXNWXkJgnFkUCt7o0jEsDl7wZE6v860rIobZy4"

# Speciali rolė administracinėms / testavimo / konkursų komandoms
SPECIAL_ROLE_ID = 1553439023576653906

# Automatinio welcome kanalas
WELCOME_CHANNEL_ID = 1553455176860307647

# Verifikacija
VERIFICATION_CHANNEL_ID = 1553460720447000667
VERIFICATION_ROLE_ID = 1553439023576653906

# Ticket sistema
TICKET_PANEL_CHANNEL_ID = 1553454051461435484
TICKET_SUPPORT_ROLE_ID = 1553439023576653906
TICKET_CATEGORY_NAME = "🎫 TICKETAI"

# Konkursų sistema
CONTEST_CHANNEL_ID = 1553453857042997278
CONTEST_ROLE_ID = 1553439023576653906
CONTEST_REACTION = "🎉"

# Konkursų duomenys
CONTESTS_FILE = "konkursai.json"


# =========================================================
# BOT NUSTATYMAI
# =========================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

startup_done = False
verification_message_id = None
contest_task_started = False


# =========================================================
# BENDROS PAGALBINĖS FUNKCIJOS
# =========================================================

def turi_role(
    member: discord.Member,
    role_id: int
) -> bool:
    return any(
        role.id == role_id
        for role in member.roles
    )


def turi_specialia_role(
    member: discord.Member
) -> bool:
    return turi_role(
        member,
        SPECIAL_ROLE_ID
    )


def turi_support_role(
    member: discord.Member
) -> bool:
    return turi_role(
        member,
        TICKET_SUPPORT_ROLE_ID
    )


# =========================================================
# WELCOME
# =========================================================

@bot.event
async def on_member_join(
    member: discord.Member
):
    channel = bot.get_channel(
        WELCOME_CHANNEL_ID
    )

    if channel is None:
        print("❌ Nerastas welcome kanalas.")
        return

    member_count = member.guild.member_count or 0

    embed = discord.Embed(
        title="🎉 NAUJAS NARYS!",
        description=(
            f"**Sveikas atvykęs į {member.guild.name}!** 👋\n\n"
            f"{member.mention}, labai smagu tave matyti "
            "mūsų bendruomenėje! ❤️"
        ),
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.add_field(
        name="👤 Narys",
        value=member.mention,
        inline=True
    )

    embed.add_field(
        name="🔢 Narių serveryje",
        value=f"**#{member_count}**",
        inline=True
    )

    embed.add_field(
        name="🆔 Vartotojo ID",
        value=f"`{member.id}`",
        inline=False
    )

    embed.set_footer(
        text=f"{member.guild.name} • Narys #{member_count}"
    )

    embed.timestamp = discord.utils.utcnow()

    try:
        await channel.send(
            content=member.mention,
            embed=embed,
            allowed_mentions=discord.AllowedMentions(
                users=True
            )
        )

        print(
            f"✅ Welcome išsiųstas: {member}"
        )

    except discord.Forbidden:
        print(
            "❌ Botas neturi teisės rašyti į welcome kanalą."
        )

    except discord.HTTPException as error:
        print(
            f"❌ Welcome klaida: {error}"
        )


# =========================================================
# PREFIX KOMANDŲ TEISĖS
# =========================================================

@bot.check
async def special_role_check(
    ctx: commands.Context
):
    if not isinstance(
        ctx.author,
        discord.Member
    ):
        return False

    return turi_specialia_role(
        ctx.author
    )


# =========================================================
# !LABAS
# =========================================================

@bot.command()
async def labas(
    ctx: commands.Context
):
    await ctx.send(
        "Labas! 👋"
    )


# =========================================================
# !TESTWELCOME
# =========================================================

@bot.command()
async def testwelcome(
    ctx: commands.Context
):
    channel = bot.get_channel(
        WELCOME_CHANNEL_ID
    )

    if channel is None:
        await ctx.send(
            "❌ Nerastas welcome kanalas."
        )
        return

    member_count = ctx.guild.member_count or 0

    embed = discord.Embed(
        title="🎉 NAUJAS NARYS!",
        description=(
            f"**Sveikas atvykęs į {ctx.guild.name}!** 👋\n\n"
            f"{ctx.author.mention}, labai smagu tave matyti "
            "mūsų bendruomenėje! ❤️"
        ),
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(
        url=ctx.author.display_avatar.url
    )

    embed.add_field(
        name="👤 Narys",
        value=ctx.author.mention,
        inline=True
    )

    embed.add_field(
        name="🔢 Narių serveryje",
        value=f"**#{member_count}**",
        inline=True
    )

    embed.add_field(
        name="🆔 Vartotojo ID",
        value=f"`{ctx.author.id}`",
        inline=False
    )

    embed.set_footer(
        text=f"{ctx.guild.name} • Narys #{member_count}"
    )

    embed.timestamp = discord.utils.utcnow()

    try:
        await channel.send(
            content=ctx.author.mention,
            embed=embed,
            allowed_mentions=discord.AllowedMentions(
                users=True
            )
        )

        await ctx.send(
            "✅ Testinė welcome žinutė išsiųsta.",
            delete_after=5
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Botas negali rašyti į welcome kanalą."
        )


# =========================================================
# PREFIX KOMANDŲ KLAIDOS
# =========================================================

@bot.event
async def on_command_error(
    ctx: commands.Context,
    error: commands.CommandError
):
    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    if isinstance(
        error,
        commands.CheckFailure
    ):
        try:
            await ctx.send(
                "❌ Neturi reikiamos specialios rolės.",
                delete_after=5
            )
        except discord.HTTPException:
            pass

        return

    print(
        f"❌ Komandos klaida: {error}"
    )


# =========================================================
# /ZINUTE
# =========================================================

class ZinuteModal(
    discord.ui.Modal
):
    def __init__(self):
        super().__init__(
            title="📢 Sukurti Embed žinutę"
        )

    pavadinimas = discord.ui.TextInput(
        label="Embed pavadinimas",
        placeholder="Pvz. 📢 Svarbi informacija",
        required=True,
        max_length=256
    )

    tekstas = discord.ui.TextInput(
        label="Žinutė",
        placeholder="Parašyk visą žinutę...",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=4000
    )

    tagas = discord.ui.TextInput(
        label="Tagas (nebūtina)",
        placeholder="Pvz. <@123456789>",
        required=False,
        max_length=100
    )

    footer = discord.ui.TextInput(
        label="Apačia (nebūtina)",
        placeholder="Pvz. PurityRP • Administracija",
        required=False,
        max_length=2048
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title=self.pavadinimas.value,
            description=self.tekstas.value,
            color=discord.Color.blurple()
        )

        if self.footer.value.strip():
            embed.set_footer(
                text=self.footer.value.strip()
            )

        tagas = self.tagas.value.strip()

        try:
            if tagas:
                await interaction.channel.send(
                    content=tagas,
                    embed=embed,
                    allowed_mentions=discord.AllowedMentions(
                        users=True,
                        roles=True
                    )
                )
            else:
                await interaction.channel.send(
                    embed=embed
                )

            await interaction.response.send_message(
                "✅ Embed žinutė išsiųsta!",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Botas neturi teisės siųsti žinutės.",
                ephemeral=True
            )


@bot.tree.command(
    name="zinute",
    description="Sukurti gražią Embed žinutę"
)
async def zinute(
    interaction: discord.Interaction
):
    if not isinstance(
        interaction.user,
        discord.Member
    ):
        return

    if not turi_specialia_role(
        interaction.user
    ):
        await interaction.response.send_message(
            "❌ Neturi reikiamos specialios rolės.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(
        ZinuteModal()
    )


# =========================================================
# VERIFIKACIJA
# =========================================================

async def setup_verification_message():
    global verification_message_id

    channel = bot.get_channel(
        VERIFICATION_CHANNEL_ID
    )

    if channel is None:
        print(
            "❌ Nerastas verifikacijos kanalas."
        )
        return

    try:
        async for message in channel.history(
            limit=100
        ):
            if message.author != bot.user:
                continue

            if not message.embeds:
                continue

            if (
                message.embeds[0].title
                == "✅ Serverio verifikacija"
            ):
                verification_message_id = message.id

                has_check = any(
                    str(reaction.emoji) == "✅"
                    for reaction in message.reactions
                )

                if not has_check:
                    try:
                        await message.add_reaction(
                            "✅"
                        )
                    except discord.HTTPException:
                        pass

                print(
                    "✅ Verifikacijos žinutė jau egzistuoja."
                )
                return

    except discord.Forbidden:
        print(
            "❌ Botas negali skaityti "
            "verifikacijos kanalo."
        )
        return

    embed = discord.Embed(
        title="✅ Serverio verifikacija",
        description=(
            "**Sveiki atvykę į mūsų serverį!** 👋\n\n"
            "Norėdami patvirtinti save serveryje, "
            "paspauskite **✅** reakciją.\n\n"
            "✅ Paspaudus reakciją jums bus suteikta "
            "verifikacijos rolė."
        ),
        color=discord.Color.green()
    )

    embed.set_footer(
        text="PurityRP • Serverio verifikacija"
    )

    try:
        message = await channel.send(
            embed=embed
        )

        await message.add_reaction(
            "✅"
        )

        verification_message_id = message.id

        print(
            "✅ Verifikacijos žinutė sukurta."
        )

    except discord.Forbidden:
        print(
            "❌ Botas neturi teisių verifikacijos kanale."
        )


@bot.listen("on_raw_reaction_add")
async def verification_reaction(
    payload: discord.RawReactionActionEvent
):
    if (
        bot.user
        and payload.user_id == bot.user.id
    ):
        return

    if (
        payload.channel_id
        != VERIFICATION_CHANNEL_ID
    ):
        return

    if (
        verification_message_id is not None
        and payload.message_id
        != verification_message_id
    ):
        return

    if str(payload.emoji) != "✅":
        return

    guild = bot.get_guild(
        payload.guild_id
    )

    if guild is None:
        return

    member = guild.get_member(
        payload.user_id
    )

    if member is None:
        try:
            member = await guild.fetch_member(
                payload.user_id
            )
        except discord.HTTPException:
            return

    role = guild.get_role(
        VERIFICATION_ROLE_ID
    )

    if role is None:
        print(
            "❌ Nerasta verifikacijos rolė."
        )
        return

    if guild.me is None:
        return

    if role >= guild.me.top_role:
        print(
            "❌ Verifikacijos rolė turi būti žemiau boto rolės."
        )
        return

    if role in member.roles:
        return

    try:
        await member.add_roles(
            role,
            reason="Serverio verifikacija"
        )

        print(
            f"✅ {member} gavo verifikacijos rolę."
        )

    except discord.Forbidden:
        print(
            "❌ Botas negali uždėti verifikacijos rolės."
        )


# =========================================================
# TICKET SISTEMA
# =========================================================

def yra_ticket_kanalas(
    channel: discord.TextChannel
) -> bool:
    return bool(
        channel.topic
        and channel.topic.startswith(
            "ticket_owner:"
        )
    )


def gauti_ticket_owner_id(
    channel: discord.TextChannel
):
    if not channel.topic:
        return None

    match = re.search(
        r"ticket_owner:(\d+)",
        channel.topic
    )

    if match:
        return int(match.group(1))

    return None


def gauti_claimed_id(
    channel: discord.TextChannel
) -> int:
    if not channel.topic:
        return 0

    match = re.search(
        r"claimed:(\d+)",
        channel.topic
    )

    if match:
        return int(match.group(1))

    return 0


async def rasti_esama_ticketa(
    guild: discord.Guild,
    member: discord.Member
):
    for channel in guild.text_channels:
        if not yra_ticket_kanalas(channel):
            continue

        if (
            gauti_ticket_owner_id(channel)
            == member.id
        ):
            return channel

    return None


async def gauti_ticket_kategorija(
    guild: discord.Guild
):
    category = discord.utils.get(
        guild.categories,
        name=TICKET_CATEGORY_NAME
    )

    if category is not None:
        return category

    try:
        return await guild.create_category(
            TICKET_CATEGORY_NAME,
            reason="Ticketų sistemos kategorija"
        )
    except discord.Forbidden:
        return None
    except discord.HTTPException as error:
        print(
            f"❌ Kategorijos klaida: {error}"
        )
        return None


def suformuoti_ticket_varda(
    member: discord.Member
) -> str:
    name = member.display_name.lower().strip()

    name = re.sub(
        r"\s+",
        "-",
        name
    )

    name = re.sub(
        r"[^a-z0-9ąčęėįšųūž-]",
        "",
        name
    )

    name = re.sub(
        r"-+",
        "-",
        name
    )

    name = name.strip("-")

    if not name:
        name = "user"

    return f"ticket-{name}"[:90]


# =========================================================
# TICKET PANELĖ
# =========================================================

class TicketPanelView(
    discord.ui.View
):
    def __init__(self):
        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Pakelti ticketą",
        emoji="🎫",
        style=discord.ButtonStyle.success,
        custom_id="ticket:open"
    )
    async def open_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        guild = interaction.guild

        if guild is None:
            return

        member = interaction.user

        if not isinstance(
            member,
            discord.Member
        ):
            return

        existing = await rasti_esama_ticketa(
            guild,
            member
        )

        if existing:
            await interaction.response.send_message(
                f"❌ Tu jau turi ticketą: "
                f"{existing.mention}",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            TicketCreateModal()
        )


# =========================================================
# TICKET MODAL
# =========================================================

class TicketCreateModal(
    discord.ui.Modal
):
    def __init__(self):
        super().__init__(
            title="🎫 Sukurti ticketą"
        )

    tema = discord.ui.TextInput(
        label="Tema",
        placeholder="Pvz. Pagalba dėl serverio",
        required=True,
        max_length=100
    )

    aprasymas = discord.ui.TextInput(
        label="Aprašymas",
        placeholder="Aprašyk savo problemą ar klausimą...",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=2000
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        guild = interaction.guild
        member = interaction.user

        if guild is None:
            return

        if not isinstance(
            member,
            discord.Member
        ):
            return

        existing = await rasti_esama_ticketa(
            guild,
            member
        )

        if existing:
            await interaction.response.send_message(
                f"❌ Tu jau turi ticketą: "
                f"{existing.mention}",
                ephemeral=True
            )
            return

        support_role = guild.get_role(
            TICKET_SUPPORT_ROLE_ID
        )

        if support_role is None:
            await interaction.response.send_message(
                "❌ Nerasta support rolė.",
                ephemeral=True
            )
            return

        category = await gauti_ticket_kategorija(
            guild
        )

        if category is None:
            await interaction.response.send_message(
                "❌ Nepavyko sukurti ticket kategorijos.",
                ephemeral=True
            )
            return

        channel_name = suformuoti_ticket_varda(
            member
        )

        original_name = channel_name
        counter = 2

        while discord.utils.get(
            guild.text_channels,
            name=channel_name
        ) is not None:

            suffix = f"-{counter}"

            channel_name = (
                original_name[
                    :100 - len(suffix)
                ]
                + suffix
            )

            counter += 1

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            member:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                ),

            support_role:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                ),

            guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True,
                    manage_channels=True,
                    manage_messages=True
                )
        }

        try:
            ticket_channel = await guild.create_text_channel(
                channel_name,
                category=category,
                overwrites=overwrites,
                topic=(
                    f"ticket_owner:{member.id}"
                    f"|claimed:0"
                ),
                reason=f"Ticket sukūrė {member}"
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Botui trūksta **Manage Channels** teisės.",
                ephemeral=True
            )
            return

        except discord.HTTPException as error:
            print(
                f"❌ Ticket kūrimo klaida: {error}"
            )

            await interaction.response.send_message(
                "❌ Nepavyko sukurti ticketo.",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title="🎫 Ticketas sukurtas",
            description=(
                f"Sveikas, {member.mention}! 👋\n\n"
                "Tavo užklausa sėkmingai sukurta.\n"
                "Palauk, kol su tavimi susisieks "
                "pagalbos komanda."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="📌 Tema",
            value=self.tema.value,
            inline=False
        )

        embed.add_field(
            name="📝 Aprašymas",
            value=self.aprasymas.value,
            inline=False
        )

        embed.add_field(
            name="👤 Sukūrė",
            value=member.mention,
            inline=True
        )

        embed.add_field(
            name="🛠️ Pagalba",
            value=support_role.mention,
            inline=True
        )

        embed.set_footer(
            text="PurityRP • Ticketų sistema"
        )

        try:
            await ticket_channel.send(
                content=(
                    f"{member.mention} "
                    f"{support_role.mention}\n"
                    "📨 **Naujas ticketas!**"
                ),
                embed=embed,
                view=TicketControlView()
            )

        except discord.Forbidden:

            try:
                await ticket_channel.delete(
                    reason="Nepavyko išsiųsti ticket žinutės"
                )
            except discord.HTTPException:
                pass

            await interaction.response.send_message(
                "❌ Botas negali rašyti ticket kanale.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            f"✅ Tavo ticketas sukurtas: "
            f"{ticket_channel.mention}",
            ephemeral=True
        )


# =========================================================
# TICKET KONTROLĖ
# =========================================================

class TicketControlView(
    discord.ui.View
):
    def __init__(self):
        super().__init__(
            timeout=None
        )

    # -----------------------------------------------------
    # APSIIMTI
    # -----------------------------------------------------

    @discord.ui.button(
        label="Apsiimti",
        emoji="🛠️",
        style=discord.ButtonStyle.primary,
        custom_id="ticket:claim"
    )
    async def claim_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        member = interaction.user
        channel = interaction.channel

        if not isinstance(
            member,
            discord.Member
        ):
            return

        if not isinstance(
            channel,
            discord.TextChannel
        ):
            return

        if not turi_support_role(
            member
        ):
            await interaction.response.send_message(
                "❌ Tik support komanda gali apsiimti ticketą.",
                ephemeral=True
            )
            return

        if not yra_ticket_kanalas(
            channel
        ):
            await interaction.response.send_message(
                "❌ Tai nėra ticket kanalas.",
                ephemeral=True
            )
            return

        claimed_id = gauti_claimed_id(
            channel
        )

        if claimed_id:

            claimed_member = (
                channel.guild.get_member(
                    claimed_id
                )
            )

            if claimed_member:

                await interaction.response.send_message(
                    f"❌ Šį ticketą jau apsiėmė "
                    f"{claimed_member.mention}.",
                    ephemeral=True
                )

            else:

                await interaction.response.send_message(
                    "❌ Šį ticketą jau apsiėmė kitas darbuotojas.",
                    ephemeral=True
                )

            return

        owner_id = gauti_ticket_owner_id(
            channel
        )

        try:
            await channel.edit(
                topic=(
                    f"ticket_owner:{owner_id}"
                    f"|claimed:{member.id}"
                )
            )

        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ Nepavyko apsiimti ticketo.",
                ephemeral=True
            )
            return

        button.disabled = True

        try:
            await interaction.response.edit_message(
                view=self
            )
        except discord.NotFound:
            pass
        except discord.HTTPException:
            pass

        try:
            await channel.send(
                f"🛠️ Šį ticketą apsiėmė "
                f"{member.mention}."
            )
        except discord.HTTPException:
            pass

    # -----------------------------------------------------
    # UŽDARYTI
    # -----------------------------------------------------

    @discord.ui.button(
        label="Uždaryti",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="ticket:close"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        member = interaction.user
        channel = interaction.channel

        if not isinstance(
            member,
            discord.Member
        ):
            return

        if not isinstance(
            channel,
            discord.TextChannel
        ):
            return

        if not yra_ticket_kanalas(
            channel
        ):
            await interaction.response.send_message(
                "❌ Tai nėra ticket kanalas.",
                ephemeral=True
            )
            return

        owner_id = gauti_ticket_owner_id(
            channel
        )

        if (
            member.id != owner_id
            and not turi_support_role(member)
        ):
            await interaction.response.send_message(
                "❌ Ticketą gali uždaryti tik jo autorius "
                "arba support komanda.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            (
                "⚠️ **Ar tikrai norite uždaryti šį ticketą?**\n\n"
                "Paspaudus **Taip, uždaryti**, "
                "kanalas bus ištrintas po **10 sekundžių**."
            ),
            view=CloseConfirmationView(),
            ephemeral=True
        )


# =========================================================
# TICKET UŽDARYMO PATVIRTINIMAS
# =========================================================

class CloseConfirmationView(
    discord.ui.View
):
    def __init__(self):
        super().__init__(
            timeout=30
        )

    @discord.ui.button(
        label="Taip, uždaryti",
        emoji="✅",
        style=discord.ButtonStyle.danger
    )
    async def confirm_close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        channel = interaction.channel

        if not isinstance(
            channel,
            discord.TextChannel
        ):
            return

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content=(
                "🔒 **Ticketas uždaromas!**\n\n"
                "⏳ Kanalas bus ištrintas po **10 sekundžių**."
            ),
            view=self
        )

        await asyncio.sleep(10)

        try:
            await channel.delete(
                reason=f"Ticket uždarė {interaction.user}"
            )

            print(
                f"✅ Ticket {channel.name} ištrintas."
            )

        except discord.NotFound:
            print(
                "ℹ️ Ticket kanalas jau buvo ištrintas."
            )

        except discord.Forbidden:
            print(
                "❌ Botas neturi Manage Channels teisės."
            )

        except discord.HTTPException as error:
            print(
                f"❌ Ticket trynimo klaida: {error}"
            )

    @discord.ui.button(
        label="Atšaukti",
        emoji="❌",
        style=discord.ButtonStyle.secondary
    )
    async def cancel_close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            content="✅ **Ticketo uždarymas atšauktas.**",
            view=None
        )

        self.stop()


# =========================================================
# TICKET PANELĖS KŪRIMAS
# =========================================================

async def setup_ticket_panel():

    channel = bot.get_channel(
        TICKET_PANEL_CHANNEL_ID
    )

    if channel is None:
        print(
            "❌ Nerastas ticket panelės kanalas."
        )
        return

    try:
        async for message in channel.history(
            limit=100
        ):
            if message.author != bot.user:
                continue

            if not message.embeds:
                continue

            if (
                message.embeds[0].title
                == "🎫 Reikia pagalbos?"
            ):
                print(
                    "✅ Ticket panelė jau egzistuoja."
                )
                return

    except discord.Forbidden:
        print(
            "❌ Botas negali skaityti ticket panelės kanalo."
        )
        return

    embed = discord.Embed(
        title="🎫 Reikia pagalbos?",
        description=(
            "Sveiki atvykę į mūsų pagalbos centrą! 👋\n\n"
            "Norėdami susisiekti su administracija "
            "ar pagalbos komanda, paspauskite "
            "**Pakelti ticketą**.\n\n"
            "**📌 Kaip veikia ticketai?**\n\n"
            "1️⃣ Paspauskite **Pakelti ticketą**\n"
            "2️⃣ Užpildykite atsiradusią lentelę\n"
            "3️⃣ Bus sukurtas privatus kanalas\n"
            "4️⃣ Palaukite pagalbos komandos\n\n"
            "🔒 Ticketą matys tik jūs ir pagalbos komanda."
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🛠️ Pagalbos komanda",
        value=f"<@&{TICKET_SUPPORT_ROLE_ID}>",
        inline=False
    )

    embed.set_footer(
        text="PurityRP • Ticketų sistema"
    )

    try:
        await channel.send(
            embed=embed,
            view=TicketPanelView()
        )

        print(
            "✅ Ticket panelė sukurta."
        )

    except discord.Forbidden:
        print(
            "❌ Botas negali siųsti ticket panelės."
        )


# =========================================================
# KONKURSŲ DUOMENYS
# =========================================================

def load_contests():

    try:
        with open(
            CONTESTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except FileNotFoundError:
        return {}

    except json.JSONDecodeError:
        print(
            "⚠️ konkursai.json sugadintas. "
            "Pradedama nuo tuščio sąrašo."
        )
        return {}

    except Exception as error:
        print(
            f"❌ Konkursų įkėlimo klaida: {error}"
        )
        return {}


def save_contests(
    data
):

    try:
        with open(
            CONTESTS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

    except Exception as error:
        print(
            f"❌ Konkursų išsaugojimo klaida: {error}"
        )


contests = load_contests()


# =========================================================
# KONKURSO LAIKO PARSINIMAS
# =========================================================

def parse_contest_time(
    text: str
):
    text = text.strip()

    formats = [
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%d.%m.%Y %H:%M",
        "%d-%m-%Y %H:%M"
    ]

    for date_format in formats:

        try:
            parsed = datetime.strptime(
                text,
                date_format
            )

            # Įrašytas laikas laikomas Lietuvos laiku:
            # UTC+3 vasaros metu.
            # Kadangi botas dabar kuriamas 2026 m. vasarai,
            # tai atitinka dabartinį Lietuvos laiką.
            return parsed.replace(
                tzinfo=timezone(
                    timedelta(hours=3)
                )
            )

        except ValueError:
            continue

    return None


# =========================================================
# KONKURSO EMBED
# =========================================================

def create_contest_embed(
    data,
    ended=False
):

    end_time = datetime.fromisoformat(
        data["end_time"]
    )

    end_timestamp = int(
        end_time.timestamp()
    )

    if ended:
        title = (
            f"🏁 {data['title']} – BAIGĖSI"
        )
        status = "🔴 Baigėsi"
    else:
        title = f"🎉 {data['title']}"
        status = "🟢 Vyksta"

    embed = discord.Embed(
        title=title,
        description=data["description"],
        color=discord.Color.gold()
    )

    embed.add_field(
        name="🏆 Prizai",
        value=data["prizes"],
        inline=False
    )

    embed.add_field(
        name="⏰ Pabaiga",
        value=(
            f"<t:{end_timestamp}:F>\n"
            f"<t:{end_timestamp}:R>"
        ),
        inline=False
    )

    if not ended:
        embed.add_field(
            name="🎟️ Kaip dalyvauti?",
            value=(
                "Paspauskite **🎉** reakciją "
                "po šia žinute ir būsite "
                "įtraukti į dalyvių sąrašą!"
            ),
            inline=False
        )

    embed.add_field(
        name="👥 Dalyviai",
        value=str(
            len(
                data.get(
                    "participants",
                    []
                )
            )
        ),
        inline=True
    )

    embed.add_field(
        name="📌 Statusas",
        value=status,
        inline=True
    )

    embed.set_footer(
        text="PurityRP • Konkursų sistema"
    )

    return embed


# =========================================================
# KONKURSO MODAL
# =========================================================

class ContestModal(
    discord.ui.Modal
):

    def __init__(self):
        super().__init__(
            title="🎉 Sukurti konkursą"
        )

    pavadinimas = discord.ui.TextInput(
        label="Konkurso pavadinimas",
        placeholder="Pvz. 🎁 50€ konkursas",
        required=True,
        max_length=256
    )

    pabaiga = discord.ui.TextInput(
        label="Iki kada vyks?",
        placeholder="Pvz. 2026-10-10 20:00",
        required=True,
        max_length=30
    )

    aprasymas = discord.ui.TextInput(
        label="Aprašymas",
        placeholder="Konkurso taisyklės ir informacija...",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=4000
    )

    prizai = discord.ui.TextInput(
        label="Prizai",
        placeholder="Pvz. 1 vieta – 50€, 2 vieta – VIP",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=1500
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        end_time = parse_contest_time(
            self.pabaiga.value
        )

        if end_time is None:
            await interaction.response.send_message(
                (
                    "❌ Neteisingas datos formatas.\n\n"
                    "Naudok:\n"
                    "`YYYY-MM-DD HH:MM`\n\n"
                    "Pvz.:\n"
                    "`2026-10-10 20:00`"
                ),
                ephemeral=True
            )
            return

        now = datetime.now(
            end_time.tzinfo
        )

        if end_time <= now:
            await interaction.response.send_message(
                "❌ Konkurso pabaiga turi būti ateityje.",
                ephemeral=True
            )
            return

        contest_data = {
            "guild_id": interaction.guild.id,
            "channel_id": CONTEST_CHANNEL_ID,
            "title": self.pavadinimas.value,
            "description": self.aprasymas.value,
            "prizes": self.prizai.value,
            "end_time": end_time.isoformat(),
            "participants": [],
            "ended": False,
            "winner_id": None,
            "message_id": None
        }

        embed = create_contest_embed(
            contest_data
        )

        try:
            message = await interaction.channel.send(
                embed=embed
            )

            await message.add_reaction(
                CONTEST_REACTION
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Botas neturi teisių šiame kanale.",
                ephemeral=True
            )
            return

        except discord.HTTPException as error:
            print(
                f"❌ Konkurso kūrimo klaida: {error}"
            )

            await interaction.response.send_message(
                "❌ Nepavyko sukurti konkurso.",
                ephemeral=True
            )

            return

        contest_data["message_id"] = message.id

        contests[str(message.id)] = contest_data

        save_contests(
            contests
        )

        await interaction.response.send_message(
            "✅ Konkursas sėkmingai sukurtas!",
            ephemeral=True
        )


# =========================================================
# /KONKURSAS
# =========================================================

@bot.tree.command(
    name="konkursas",
    description="Sukurti naują konkursą"
)
async def konkursas(
    interaction: discord.Interaction
):

    if interaction.channel_id != CONTEST_CHANNEL_ID:
        await interaction.response.send_message(
            (
                "❌ Šią komandą galima naudoti tik "
                f"<#{CONTEST_CHANNEL_ID}>."
            ),
            ephemeral=True
        )
        return

    if not isinstance(
        interaction.user,
        discord.Member
    ):
        return

    if not turi_role(
        interaction.user,
        CONTEST_ROLE_ID
    ):
        await interaction.response.send_message(
            "❌ Neturi reikiamos rolės konkursams.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(
        ContestModal()
    )


# =========================================================
# KONKURSO DALYVAVIMAS
# =========================================================

@bot.listen("on_raw_reaction_add")
async def contest_reaction_add(
    payload: discord.RawReactionActionEvent
):

    if (
        bot.user
        and payload.user_id == bot.user.id
    ):
        return

    if (
        payload.channel_id
        != CONTEST_CHANNEL_ID
    ):
        return

    if str(payload.emoji) != CONTEST_REACTION:
        return

    contest = contests.get(
        str(payload.message_id)
    )

    if contest is None:
        return

    if contest.get("ended"):
        return

    if payload.user_id not in contest["participants"]:

        contest["participants"].append(
            payload.user_id
        )

        save_contests(
            contests
        )

        try:
            channel = bot.get_channel(
                CONTEST_CHANNEL_ID
            )

            if channel is not None:

                message = await channel.fetch_message(
                    payload.message_id
                )

                await message.edit(
                    embed=create_contest_embed(
                        contest
                    )
                )

        except discord.HTTPException:
            pass


@bot.listen("on_raw_reaction_remove")
async def contest_reaction_remove(
    payload: discord.RawReactionActionEvent
):

    if (
        payload.channel_id
        != CONTEST_CHANNEL_ID
    ):
        return

    if str(payload.emoji) != CONTEST_REACTION:
        return

    contest = contests.get(
        str(payload.message_id)
    )

    if contest is None:
        return

    if contest.get("ended"):
        return

    if payload.user_id in contest["participants"]:

        contest["participants"].remove(
            payload.user_id
        )

        save_contests(
            contests
        )

        try:
            channel = bot.get_channel(
                CONTEST_CHANNEL_ID
            )

            if channel is not None:

                message = await channel.fetch_message(
                    payload.message_id
                )

                await message.edit(
                    embed=create_contest_embed(
                        contest
                    )
                )

        except discord.HTTPException:
            pass


# =========================================================
# KONKURSO PABAIGA
# =========================================================

async def finish_contest(
    contest_id,
    contest
):

    if contest.get("ended"):
        return

    guild = bot.get_guild(
        contest["guild_id"]
    )

    if guild is None:
        return

    channel = bot.get_channel(
        contest["channel_id"]
    )

    if channel is None:
        return

    valid_participants = []

    for user_id in contest.get(
        "participants",
        []
    ):

        member = guild.get_member(
            user_id
        )

        if member is None:
            try:
                member = await guild.fetch_member(
                    user_id
                )
            except discord.HTTPException:
                continue

        if member.bot:
            continue

        valid_participants.append(
            member
        )

    contest["ended"] = True

    # -----------------------------------------------------
    # NĖRA DALYVIŲ
    # -----------------------------------------------------

    if not valid_participants:

        contest["winner_id"] = None

        save_contests(
            contests
        )

        try:
            original_message = (
                await channel.fetch_message(
                    int(contest_id)
                )
            )

            embed = create_contest_embed(
                contest,
                ended=True
            )

            embed.add_field(
                name="🏆 Rezultatas",
                value=(
                    "❌ Konkursas baigėsi, "
                    "bet nebuvo dalyvių."
                ),
                inline=False
            )

            await original_message.edit(
                embed=embed
            )

            await channel.send(
                embed=discord.Embed(
                    title="🏁 Konkursas baigėsi",
                    description=(
                        f"**{contest['title']}** baigėsi, "
                        "tačiau dalyvių nebuvo."
                    ),
                    color=discord.Color.red()
                )
            )

        except discord.HTTPException:
            pass

        return

    # -----------------------------------------------------
    # RANDOM LAIMĖTOJAS
    # -----------------------------------------------------

    winner = random.choice(
        valid_participants
    )

    contest["winner_id"] = winner.id

    save_contests(
        contests
    )

    # -----------------------------------------------------
    # ORIGINALI KONKURSO ŽINUTĖ
    # -----------------------------------------------------

    try:
        original_message = (
            await channel.fetch_message(
                int(contest_id)
            )
        )

        embed = create_contest_embed(
            contest,
            ended=True
        )

        embed.add_field(
            name="🏆 Laimėtojas",
            value=winner.mention,
            inline=False
        )

        await original_message.edit(
            embed=embed
        )

    except discord.HTTPException:
        pass

    # -----------------------------------------------------
    # LAIMĖTOJO PASKELBIMAS
    # -----------------------------------------------------

    winner_embed = discord.Embed(
        title="🏆 TURIME LAIMĖTOJĄ!",
        description=(
            f"🎉 Sveikiname {winner.mention}!\n\n"
            f"Tu laimėjai konkursą "
            f"**{contest['title']}**!\n\n"
            f"🎁 **Prizas:**\n"
            f"{contest['prizes']}\n\n"
            "📩 Prizo atsiėmimui pakelk ticketą "
            "mūsų ticketų kanale:\n"
            f"<#{TICKET_PANEL_CHANNEL_ID}>"
        ),
        color=discord.Color.gold()
    )

    winner_embed.set_footer(
        text="PurityRP • Konkursų sistema"
    )

    try:
        await channel.send(
            content=winner.mention,
            embed=winner_embed,
            allowed_mentions=discord.AllowedMentions(
                users=True
            )
        )

    except discord.HTTPException:
        pass


# =========================================================
# KONKURSŲ CHECKER
# =========================================================

async def contest_checker():

    await bot.wait_until_ready()

    while not bot.is_closed():

        now = datetime.now(
            timezone.utc
        )

        changed = False

        for contest_id, contest in list(
            contests.items()
        ):

            if contest.get("ended"):
                continue

            try:
                end_time = datetime.fromisoformat(
                    contest["end_time"]
                )

            except (
                ValueError,
                KeyError,
                TypeError
            ):
                contest["ended"] = True
                changed = True
                continue

            # Palyginimui konvertuojame į UTC
            if end_time.tzinfo is not None:
                end_time_utc = end_time.astimezone(
                    timezone.utc
                )
            else:
                end_time_utc = end_time.replace(
                    tzinfo=timezone.utc
                )

            if now >= end_time_utc:

                await finish_contest(
                    contest_id,
                    contest
                )

                changed = True

        if changed:
            save_contests(
                contests
            )

        await asyncio.sleep(20)


# =========================================================
# BOT PALEIDIMAS
# =========================================================

@bot.event
async def on_ready():

    global startup_done
    global contest_task_started

    if startup_done:
        return

    startup_done = True

    print("=" * 60)

    print(
        f"✅ Botas prisijungė kaip {bot.user}"
    )

    print(
        f"✅ Serverių: {len(bot.guilds)}"
    )

    print("=" * 60)

    # -----------------------------------------------------
    # TICKET MYGTUKAI
    # -----------------------------------------------------

    bot.add_view(
        TicketPanelView()
    )

    bot.add_view(
        TicketControlView()
    )

    print(
        "✅ Ticket mygtukai aktyvuoti."
    )

    # -----------------------------------------------------
    # SLASH KOMANDOS
    # -----------------------------------------------------

    total_synced = 0

    try:

        for guild in bot.guilds:

            bot.tree.copy_global_to(
                guild=guild
            )

            synced = await bot.tree.sync(
                guild=guild
            )

            total_synced += len(
                synced
            )

        print(
            f"✅ Slash komandų sinchronizuota: "
            f"{total_synced}"
        )

    except Exception as error:

        print(
            f"❌ Slash komandų klaida: {error}"
        )

    # -----------------------------------------------------
    # VERIFIKACIJA
    # -----------------------------------------------------

    await setup_verification_message()

    # -----------------------------------------------------
    # TICKET PANELĖ
    # -----------------------------------------------------

    await setup_ticket_panel()

    # -----------------------------------------------------
    # KONKURSAI
    # -----------------------------------------------------

    if not contest_task_started:

        contest_task_started = True

        asyncio.create_task(
            contest_checker()
        )

        print(
            "✅ Konkursų sistema paleista."
        )

    print(
        "✅ VISOS SISTEMOS PALEISTOS!"
    )

    print("=" * 60)


# =========================================================
# PALEIDIMAS
# =========================================================

if not TOKEN or TOKEN.startswith(
    "ĮKLIJUOK_"
):
    raise ValueError(
        "❌ Į bot.py įrašyk naują Discord boto Tokeną."
    )

bot.run(TOKEN)
