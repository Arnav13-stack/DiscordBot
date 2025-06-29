import discord
from discord.ext import commands, tasks 
import config
import requests
from datetime import datetime, timedelta
from discord import app_commands
import asyncio
import random
import pytz
from collections import defaultdict
from discord.ui import Button, View, Select

# Then you can call `now()` method on it
now = datetime.now()  # This works fine now

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

# Set the ID of the "player info" channel
PLAYER_INFO_CHANNEL_ID = 1334023680539234326  # Replace with the actual channel ID

# Set the giveaway channel ID (optional: you can restrict it to a specific channel)
GIVEAWAY_CHANNEL_ID = 1334144519192711290  # Replace with your actual giveaway channel ID

# Dictionary to store invite counts
invite_counts = defaultdict(int)

# Dictionary to store invite codes and their inviters
invite_data = {}

# Dictionary to track muted users and their unmute time
muted_users = {}

# This dictionary will track event information and attendees
events = {}

# Set the ID of the "invite tracker" channel
INVITE_TRACKER_CHANNEL_ID = 1334197693601546301  # Replace with the actual channel ID

# TICKET_CHANNEL_ID = 1336883855973417051  # Replace with the actual ticket channel ID


@bot.event
async def on_ready():
    print('Bot is ready.')
    await bot.tree.sync()
    # Fetch all invites and store them in invite_data
    for guild in bot.guilds:
        invites = await guild.invites()
        for invite in invites:
            invite_data[invite.code] = invite


#invite-tracker
@bot.event
async def on_member_join(member: discord.Member):
    # Fetch the invite tracker channel
    channel = member.guild.get_channel(INVITE_TRACKER_CHANNEL_ID)
    
    if not channel:
        return

    # Fetch all invites and compare them to find the used invite
    invites = await member.guild.invites()
    for invite in invites:
        if invite_data.get(invite.code) and invite.uses > invite_data[invite.code].uses:
            inviter = invite.inviter
            invite_counts[inviter.id] += 1
            invite_data[invite.code] = invite

            # Create an embed for the join message
            embed = discord.Embed(
                title="🎉 New Member Joined!",
                description=f"{member.mention} has joined the server.",
                color=0x00FF00
            )
            embed.add_field(name="Invited By", value=f"{inviter.mention} (Total Invites: {invite_counts[inviter.id]})", inline=False)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
            embed.set_footer(text="Developed by **devil_gamer07**")

            await channel.send(embed=embed)
            break

@bot.event
async def on_member_remove(member: discord.Member):
    # Fetch the invite tracker channel
    channel = member.guild.get_channel(INVITE_TRACKER_CHANNEL_ID)
    
    if not channel:
        return

    # Find the inviter of the member who left
    for inviter_id, count in invite_counts.items():
        if member.id in invite_data:
            inviter = member.guild.get_member(inviter_id)
            if inviter:
                # Create an embed for the leave message
                embed = discord.Embed(
                    title="😢 Member Left",
                    description=f"{member.mention} has left the server.",
                    color=0xFF0000
                )
                embed.add_field(name="Invited By", value=f"{inviter.mention} (Total Invites: {invite_counts[inviter.id]})", inline=False)
                embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
                embed.set_footer(text="Developed by **devil_gamer07**")

                await channel.send(embed=embed)
                break

@bot.tree.command(name="invites", description="Check how many invites you have.")
async def invites(interaction: discord.Interaction):
    """Check how many invites you have."""
    inviter_id = interaction.user.id
    count = invite_counts.get(inviter_id, 0)

    # Create an embed for the invite count
    embed = discord.Embed(
        title="🎟️ Invite Count",
        description=f"You have invited {count} members to the server.",
        color=0x00FF00
    )
    # Create the non-clickable button below the embed
    button = discord.ui.Button(label="Developed by **devil_gamer07**", style=discord.ButtonStyle.secondary, disabled=True)  # Non-clickable button

    # Create a view to add the button
    view = discord.ui.View()
    view.add_item(button)

    # Send the embed with the non-clickable button
    await interaction.response.send_message(embed=embed, view=view)


#channel create
@bot.event
async def on_guild_channel_create(channel : discord.abc.GuildChannel):
    print("channel created")
    print(channel.name)

@bot.event
async def on_guild_channel_create(channel: discord.abc.GuildChannel):
    print("channel created")
    print(channel.name)

#welcome
@bot.event
async def on_member_join(member: discord.Member):
    # Set the channel ID for the welcome message
    channel_id = 1333797351340511262  # Replace this with your actual channel ID
    channel = member.guild.get_channel(channel_id)

    if channel:
        # Create an embed for the welcome message
        embed = discord.Embed(
            title="🎉 Welcome to the Server!",
            description=(
                f"Hi {member.mention}, welcome to **{member.guild.name}**! "
                f"Feel free to check out {channel.mention} and introduce yourself. "
                "We're excited to have you here!"
            ),
            color=0x00FFB3
        )

        # Add member avatar as thumbnail
        embed.set_thumbnail(url=member.avatar.url if member.avatar else "")

        # Add image (e.g., a welcome banner)
        embed.set_image(
            url="https://play-lh.googleusercontent.com/89hTpg_gH9N0k4u7PzIHOdbZSxstaBHx93GlFt6gyndHFblJKLR7YoS20LdQHg4h9vg=w648-h364-rw") # Replace with your image URL
        

        # Set footer with server icon and welcome text
        embed.set_footer(
            text="Welcome to the community!",
            icon_url=member.guild.icon.url if member.guild.icon else ""  # Add server icon in the footer
        )

        # Send the embed
        await channel.send(content=f"Welcome {member.mention} to **{member.guild.name}**!", embed=embed)

@bot.event
async def on_guild_role_delete(role : discord.Role):
    print("role deleted")
    print(role.name)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong 🏓!")      

# New /avatar command using slash command
@bot.tree.command(name="avatar", description="Display the avatar of the mentioned user or the command user.")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    """Sends the avatar of the mentioned user or the command user."""
    
    # Check if the command is used in the specified "player info" channel
    if interaction.channel.id != PLAYER_INFO_CHANNEL_ID:
        return await interaction.response.send_message("This command can only be used in the player info channel.", ephemeral=True)

    if member is None:
        member = interaction.user  # If no member is mentioned, use the user who invoked the command

    # Get user account type (whether the user is a bot)
    account_type = "Bot" if member.bot else "Normal"

    # Get the current time of the request
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    # Create an embed to display the avatar and user details
    embed = discord.Embed(
        title=f"{member.display_name}'s Avatar",  # Title with the member's display name
        description=(
            f"**User ID**: {member.id}\n"
            f"**Account Type**: {account_type}\n"
            f"**Avatar URL**: [Click here]({member.avatar.url})"
        ),
        color=0x00FFB3
    )
    
    # Set server thumbnail (guild icon) as the embed thumbnail
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else "")

    # Set the avatar image
    embed.set_image(url=member.avatar.url)  # Set the member's avatar as the image in the embed

    # Add footer with server icon, requested by user, and current time
    embed.set_footer(
        text=f"Requested by: {interaction.user.display_name} | Requested at: {current_time}",
        icon_url=interaction.guild.icon.url if interaction.guild.icon else ""  # Server icon in the footer
    )

    await interaction.response.send_message(embed=embed)  # Send the embed


@bot.tree.command()
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hi!")

@bot.tree.command()
async def joy(interaction: discord.Interaction):
    await interaction.response.send_message("bye!", ephemeral=True)

#server icon
@bot.tree.command(name="servericon", description="Display the server's icon.")
async def server_icon(interaction: discord.Interaction):
    """Sends the server's icon as a direct message if available, otherwise informs the user."""
    
    # Get the server's icon URL
    server_icon_url = interaction.guild.icon.url if interaction.guild.icon else None
    
    if server_icon_url:
        await interaction.response.send_message(f" {server_icon_url}")
    else:
        await interaction.response.send_message("This server doesn't have an icon set.", ephemeral=True)

#server info
@bot.tree.command(name="serverinfo", description="Display information about the server.")
async def server_info(interaction: discord.Interaction):
    """Sends an embed containing details about the server."""
    
    guild = interaction.guild  # Get the guild (server) information
    owner = guild.owner  # Get the server owner
    server_icon_url = guild.icon.url if guild.icon else None  # Get server icon
    bot_user = interaction.client.user  # Get bot's user details

    # Count online members
    online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)

    # Get server boost level
    boost_status = f"Level {guild.premium_tier} ({guild.premium_subscription_count} Boosts)"

    # Get number of roles
    roles = len(guild.roles) - 1  # Exclude @everyone role

    # Get number of channels
    total_channels = len(guild.channels)
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    category_channels = len(guild.categories)

    # Get server creation date
    created_at = guild.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')

    # Get emojis
    emoji_list = " ".join(str(emoji) for emoji in guild.emojis[:10])  # Show only first 10 emojis

    # Create embed
    embed = discord.Embed(title=f"Server Info: {guild.name}", color=0x00FFB3)
    
    embed.set_thumbnail(url=server_icon_url)  # Set server icon as thumbnail

    embed.add_field(name="👑 Owner", value=f"{owner.mention} ({owner.name}#{owner.discriminator})", inline=False)
    embed.add_field(name="🆔 Server ID", value=guild.id, inline=False)
    embed.add_field(name="🟢 Online Members", value=online_members, inline=True)
    embed.add_field(name="🚀 Boost Status", value=boost_status, inline=True)
    embed.add_field(name="🔰 Roles", value=roles, inline=True)
    embed.add_field(name="📌 Channels", value=f"Total: {total_channels}\nText: {text_channels}\nVoice: {voice_channels}\nCategories: {category_channels}", inline=False)
    embed.add_field(name="📅 Created On", value=created_at, inline=False)
    embed.add_field(name="😀 Emoji List", value=emoji_list if emoji_list else "No emojis", inline=False)

    # Footer with bot's avatar and name
    embed.set_footer(
        text=f"Requested by {interaction.user.display_name} | Bot: {bot_user.name}",
        icon_url=bot_user.avatar.url if bot_user.avatar else ""
    )

    await interaction.response.send_message(embed=embed)


#purge
@bot.tree.command(name="purge", description="Delete a specified number of messages from the channel.")
@app_commands.checks.has_permissions(manage_messages=True)  # Requires Manage Messages permission
async def purge(interaction: discord.Interaction, count: int):
    """Deletes the specified number of messages in the channel."""
    
    # Ensure count is a valid number
    if count < 1:
        return await interaction.response.send_message("❌ Please specify a number greater than 0.", ephemeral=True)

    # Defer response to avoid interaction timeout
    await interaction.response.defer(ephemeral=True)

    # Get the current channel
    channel = interaction.channel

    # Delete messages
    deleted_messages = await channel.purge(limit=count)

    # Send confirmation message
    confirmation = await interaction.followup.send(f"✅ Deleted {len(deleted_messages)} messages.", ephemeral=True)

    # Delete the confirmation message after 5 seconds
    await asyncio.sleep(5)
    await confirmation.delete()


#giveaway create
@bot.tree.command(name="giveaway", description="Create a giveaway with a set duration, winners, and prize.")
@app_commands.checks.has_permissions(manage_messages=True)  # Requires Manage Messages permission
async def giveaway(
    interaction: discord.Interaction,
    duration: str,  # Time format (e.g., "10m" for 10 minutes, "2h" for 2 hours)
    winners: int,  # Number of winners
    prize: str,  # Prize for the giveaway
    channel: discord.TextChannel = None  # Optional channel selection
):
    """Creates a giveaway with a set duration, winners, and prize."""
    
    # Determine the giveaway channel (defaults to the current channel if not specified)
    giveaway_channel = channel if channel else interaction.channel

    # Ensure a valid number of winners
    if winners < 1:
        return await interaction.response.send_message("❌ You must have at least 1 winner.", ephemeral=True)

    # Parse duration
    time_multiplier = {"m": 60, "h": 3600}
    unit = duration[-1]  # Get the last character (m or h)
    
    if unit not in time_multiplier or not duration[:-1].isdigit():
        return await interaction.response.send_message("❌ Invalid duration format. Use `Xm` for minutes or `Xh` for hours.", ephemeral=True)
    
    duration_seconds = int(duration[:-1]) * time_multiplier[unit]  # Convert duration to seconds

    # Acknowledge command
    await interaction.response.send_message(f"🎉 Giveaway created in {giveaway_channel.mention}!", ephemeral=True)

    # Create giveaway embed
    embed = discord.Embed(
        title="🎁 Giveaway Time!",
        description=(
            f"🎉 **Prize**: {prize}\n"
            f"🏆 **Winners**: {winners}\n"
            f"⏳ **Duration**: {duration}\n"
            f"🎟️ **Click the button below to enter the giveaway!**"
        ),
        color=0xFFD700,  # Gold color
        timestamp=datetime.utcnow() + timedelta(seconds=duration_seconds)
    )

    embed.set_footer(text="Ends at")  # Footer timestamp automatically updates
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else "")  # Set server icon as thumbnail
    giveaway_message = await giveaway_channel.send(embed=embed)

    # Create an "Enter Giveaway" button
    button = discord.ui.Button(label="Enter Giveaway", style=discord.ButtonStyle.green)

    # Create a view to hold the button
    view = discord.ui.View()
    view.add_item(button)

    # Send the button with the giveaway message
    await giveaway_message.edit(view=view)

    # Button click logic (enter giveaway)
    users = []
    async def on_button_click(interaction: discord.Interaction):
        # Ensure the user isn't a bot
        if interaction.user.bot:
            return

        # Add user to the entry list if not already entered
        if interaction.user not in users:
            users.append(interaction.user)
            await interaction.response.send_message(f"{interaction.user.mention} has entered the giveaway!", ephemeral=True)
        else:
            await interaction.response.send_message("You are already entered in the giveaway!", ephemeral=True)

    button.callback = on_button_click  # Assign the button click event

    # Real-time countdown update
    while duration_seconds > 0:
        remaining_time = str(timedelta(seconds=duration_seconds))
        embed.description = (
            f"🎉 **Prize**: {prize}\n"
            f"🏆 **Winners**: {winners}\n"
            f"⏳ **Remaining Time**: {remaining_time}\n"
            f"🎟️ **Click the button below to enter the giveaway!**"
        )

        # Debugging: Check if the message is getting updated
        print(f"Updating countdown to: {remaining_time}")  # Check in console

        # Update the message with the new countdown
        try:
            await giveaway_message.edit(embed=embed)
            await asyncio.sleep(2)

        except discord.errors.NotFound:
            print("Message not found! This could be due to the message being deleted.")
            break  # Stop the loop if the message was deleted

        # Wait 60 seconds before updating again
        await asyncio.sleep(60)  # Update every minute
        duration_seconds -= 60

    # After the giveaway ends, pick winners
    if len(users) < winners:
        await giveaway_channel.send(f"❌ Not enough participants for `{prize}`. Giveaway canceled.")
        return

    selected_winners = random.sample(users, winners)
    winner_mentions = ", ".join(winner.mention for winner in selected_winners)

    # Announce winners
    await giveaway_channel.send(f"🎉 Congratulations {winner_mentions}! You won **{prize}**! 🏆")

#bot invite
@bot.tree.command(name="invite", description="Get the invite link for the bot.")
async def invite_bot(interaction: discord.Interaction):
    """Sends an embed with the invite link to add the bot to another server."""
    
    # Get the bot's client ID
    bot_client_id = interaction.client.user.id
    
    # Define the required permissions (this example assumes basic permissions)
    permissions = discord.Permissions(permissions=8)  # 8 is for Administrator permissions, you can customize this
    permissions_value = permissions.value
    
    # Create the OAuth2 invite URL for the bot
    invite_url = f"https://discord.com/oauth2/authorize?client_id={bot_client_id}&scope=bot&permissions={permissions_value}"

    # Create the embed
    embed = discord.Embed(
        title="Invite Link",  # Title change
        description=f"Click here to invite the bot to your server: [Invite Link (Admin perms)]({invite_url})",  # Text change
        color=0x00FFB3
    )
    embed.set_footer(text="Invite the bot to your server and enjoy its features!")

    # Create the non-clickable button below the embed
    button = discord.ui.Button(label="Developed by **devil_gamer07**", style=discord.ButtonStyle.secondary, disabled=True)  # Non-clickable button

    # Create a view to add the button
    view = discord.ui.View()
    view.add_item(button)

    # Send the embed with the non-clickable button
    await interaction.response.send_message(embed=embed, view=view)

#poll
@bot.tree.command(name="poll", description="Create a poll with up to 10 options.")
@app_commands.describe(
    question="The poll question",
    option1="First option",
    option2="Second option (optional)",
    option3="Third option (optional)",
    option4="Fourth option (optional)",
    option5="Fifth option (optional)",
    option6="Sixth option (optional)",
    option7="Seventh option (optional)",
    option8="Eighth option (optional)",
    option9="Ninth option (optional)",
    option10="Tenth option (optional)",
    duration="Poll duration in seconds (e.g. 60, 300, etc.)",
    image_url="Optional image URL (optional)"
)
async def poll(
    interaction: discord.Interaction,
    question: str,
    option1: str,
    option2: str = None,
    option3: str = None,
    option4: str = None,
    option5: str = None,
    option6: str = None,
    option7: str = None,
    option8: str = None,
    option9: str = None,
    option10: str = None,
    duration: int = 60,
    image_url: str = None
):
    """Creates a poll with reactions for voting and duration."""

    # Defer response to prevent timeout
    await interaction.response.defer()

    options = [option for option in [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10] if option]

    if len(options) < 2:
        return await interaction.followup.send("❌ You need at least **two** options to create a poll.", ephemeral=True)

    # Define emoji numbers for options
    number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    # Create poll embed
    embed = discord.Embed(
        title="📊 Poll",
        description=f"**{question}**\n\n" + "\n".join(f"{number_emojis[i]} {option}" for i, option in enumerate(options)),
        color=0x00BFFF
    )
    if image_url:
        embed.set_image(url=image_url)
    
    embed.set_footer(text=f"Poll created by {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

    # Send poll message
    poll_message = await interaction.channel.send(embed=embed)

    # Add reactions for voting
    for i in range(len(options)):
        await poll_message.add_reaction(number_emojis[i])

    # Create a non-clickable button below the poll
    button = discord.ui.Button(label="Developed by **devil_gamer07**", style=discord.ButtonStyle.secondary, disabled=True)

    # Create a view and add the button
    view = discord.ui.View()
    view.add_item(button)

    # Show countdown and update embed periodically
    end_time = datetime.utcnow() + timedelta(seconds=duration)
    while datetime.utcnow() < end_time:
        remaining_time = end_time - datetime.utcnow()
        remaining_seconds = remaining_time.total_seconds()

        # Update countdown in the embed
        embed.description = f"**{question}**\n\n" + "\n".join(f"{number_emojis[i]} {option}" for i, option in enumerate(options)) + f"\n\n⏳ Time Remaining: {str(remaining_time).split('.')[0]}"
        await poll_message.edit(embed=embed)
        await asyncio.sleep(5)  # Update every 5 seconds

    # After time is up, send results
    results = await poll_message.channel.fetch_message(poll_message.id)
    results_count = {emoji: 0 for emoji in number_emojis[:len(options)]}
    
    for reaction in results.reactions:
        if str(reaction.emoji) in results_count:
            results_count[str(reaction.emoji)] = reaction.count - 1  # Subtract bot's own reaction

    result_embed = discord.Embed(
        title="📊 Poll Results",
        description=f"**{question}**\n\n" + "\n".join(f"{number_emojis[i]} {options[i]}: {results_count[number_emojis[i]]} votes" for i in range(len(options))),
        color=0x00BFFF
    )
    result_embed.set_footer(text=f"Poll created by {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

    # Send results in an updated embed
    await poll_message.edit(embed=result_embed, view=view)
    await interaction.followup.send("Poll has ended. Results are now available.", ephemeral=True)


#welcome bot invite
# Event when the bot joins a server
@bot.event
async def on_guild_join(guild: discord.Guild):
    # Welcome message text
    welcome_message = (
        f"Thanks for inviting {bot.user.name}! 🎉\n"
        f"{bot.user.name} is designed to simplify clan and family management while providing powerful features like legends tracking, autoboards, and in-depth stats. "
        f"It also includes tools like role management, ticketing, and roster management to make running your clan easier.\n\n"
        "Note: ClashKing is actively developed and improving constantly. If you encounter any issues or have feature suggestions, let me know! If you enjoy the bot, consider supporting the project by using Creator Code ClashKing in-game. Thank you for being part of this journey! - Destinea, Magic, & Obno ❤️"
    )

    # Get the bot's avatar URL for the thumbnail
    bot_avatar_url = bot.user.avatar.url if bot.user.avatar else "https://example.com/default-avatar.png"  # Replace with a default image URL if necessary

    # Send the welcome message in the general channel with bot image as thumbnail
    for channel in guild.text_channels:
        if channel.name == "general":  # Modify with your desired channel name
            # Create an embed with the welcome message and bot image as the thumbnail
            welcome_embed = discord.Embed(
                title=f"Thanks for inviting {bot.user.name} 🎉",
                description=welcome_message,
                color=0x2B2D31  # You can modify the color as needed
            )
            welcome_embed.set_thumbnail(url=bot_avatar_url)  # Set the bot's logo as the thumbnail

            # Send the welcome message with the embed
            await channel.send(embed=welcome_embed)
            break  # Send only to the first "general" channel found


# Warn command
# Slash command for warning
@bot.tree.command(name="warn")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    # Check if the member being warned is the bot itself
    if member == bot.user:
        await interaction.response.send_message(
            "You can't warn the bot!", ephemeral=True
        )
        return

    # Check if the member has a higher role than the bot
    if interaction.user.top_role <= member.top_role:
        await interaction.response.send_message(
            f"Sorry, {interaction.user.mention}, you cannot warn {member.mention} because they have a higher or equal role.",
            ephemeral=True
        )
        return

    # Create embed for the channel
    channel_embed = discord.Embed(
        title="Player Warned",
        description=f"{interaction.user.mention} warned {member.mention}",
        color=discord.Color.red()
    )
    channel_embed.set_thumbnail(url=member.avatar.url)  # Warned player's thumbnail
    channel_embed.add_field(name="Reason", value=reason)
    channel_embed.add_field(name="Moderator", value=interaction.user.mention)
    
    # Send the embed in the channel where the command was invoked
    await interaction.response.send_message(embed=channel_embed)

    # Send warning message to the warned player's DM
    try:
        dm_embed = discord.Embed(
            title="You have been warned!",
            description=f"You have been warned by {interaction.user.mention}",
            color=discord.Color.red()
        )
        dm_embed.set_thumbnail(url=interaction.user.avatar.url)  # Moderator's thumbnail
        dm_embed.add_field(name="Reason", value=reason)

        # Send the embed to the warned player's DM
        await member.send(embed=dm_embed)

    except discord.Forbidden:
        # Handle case if the bot can't DM the user (e.g., if the user has DMs disabled)
        await interaction.response.send_message(
            f"Could not send a DM to {member.mention}. They may have DMs disabled.",
            ephemeral=True
        )

# Synchronize commands with Discord when the bot is ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    # Sync commands with Discord
    await bot.tree.sync()


#mute
@bot.tree.command(name="mute", description="Mute a member for a specified duration (e.g., 5min, 1hour).")
@app_commands.checks.has_permissions(manage_roles=True)  # Requires Manage Roles permission
async def mute(interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
    """Mutes a member for a specific duration (e.g., '5min' or '1hour')."""

    await interaction.response.defer()  # Prevents interaction timeout

    # Check if the bot has permission to manage roles
    if not interaction.guild.me.guild_permissions.manage_roles:
        return await interaction.followup.send("❌ I don't have permission to manage roles!", ephemeral=True)

    # Get or create the mute role
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
    
    if not mute_role:
        try:
            mute_role = await interaction.guild.create_role(name="Muted", reason="Mute command used.")
            for channel in interaction.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
        except discord.Forbidden:
            return await interaction.followup.send("❌ I don't have permission to create a 'Muted' role!", ephemeral=True)

    # Check if the user is already muted
    if mute_role in member.roles:
        return await interaction.followup.send(f"{member.mention} is already muted.", ephemeral=True)

    # Convert duration to seconds
    duration_seconds = parse_duration(duration)
    if duration_seconds is None:
        return await interaction.followup.send("❌ Invalid duration format! Use '5min' or '1hour'.", ephemeral=True)

    # Add the mute role to the member
    await member.add_roles(mute_role, reason=reason)

    # Store the unmute time
    muted_users[member.id] = asyncio.get_event_loop().time() + duration_seconds

    # Send confirmation message
    embed = discord.Embed(
        title="🔇 Member Muted",
        description=f"**{member.mention}** has been muted for **{duration}**.",
        color=discord.Color.red()
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
    await interaction.followup.send(embed=embed)

    # Start the unmute process
    asyncio.create_task(unmute_after_delay(member, mute_role, duration_seconds, interaction.channel_id))


async def unmute_after_delay(member, mute_role, duration_seconds, channel_id):
    """Waits for the given duration and then unmutes the user."""
    await asyncio.sleep(duration_seconds)

    # Ensure the member is still in the server and has the mute role
    if mute_role in member.roles:
        await member.remove_roles(mute_role, reason="Mute duration expired.")

        # Get the channel and send an unmute message
        channel = bot.get_channel(channel_id)
        if channel:
            unmute_embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f"**{member.mention}** has been automatically unmuted.",
                color=discord.Color.green()
            )
            unmute_embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
            await channel.send(embed=unmute_embed)

        # Remove the user from the tracking dictionary
        muted_users.pop(member.id, None)


def parse_duration(duration: str):
    """Parses duration (e.g., '5min', '1hour') and converts it to seconds."""
    duration = duration.lower()
    if duration.endswith("min"):
        try:
            return int(duration[:-3]) * 60
        except ValueError:
            return None
    elif duration.endswith("hour"):
        try:
            return int(duration[:-4]) * 3600
        except ValueError:
            return None
    return None


#code to run mute /mute @user 10 Spamming


#unmute user
@bot.tree.command(name="unmute", description="Unmute a muted member.")
@app_commands.checks.has_permissions(manage_roles=True)  # Requires Manage Roles permission
async def unmute(interaction: discord.Interaction, member: discord.Member):
    """Unmutes a member by removing the 'Muted' role."""

    # Defer response to avoid interaction expiration
    await interaction.response.defer()

    # Check if the bot has permission to manage roles
    if not interaction.guild.me.guild_permissions.manage_roles:
        return await interaction.followup.send("❌ I don't have permission to manage roles!", ephemeral=True)

    # Get the Muted role
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")

    if not mute_role:
        return await interaction.followup.send("⚠ No 'Muted' role found. The user might not be muted.", ephemeral=True)

    # Check if the member is muted
    if mute_role not in member.roles:
        return await interaction.followup.send(f"ℹ {member.mention} is not muted.", ephemeral=True)

    # Remove the mute role
    await member.remove_roles(mute_role, reason="Unmuted by moderator")

    # Confirmation message
    embed = discord.Embed(
        title="🔊 Member Unmuted",
        description=f"**{member.mention}** has been unmuted.",
        color=discord.Color.green()
    )
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
    await interaction.followup.send(embed=embed)

#create
# Helper function: Parse event date and time
def parse_event_datetime(event_date: str, event_time: str):
    """Parse separate event date and time into a datetime object."""
    try:
        # Combine event_date and event_time into a single string
        event_str = f"{event_date} {event_time}"
        
        # Parse the combined string
        event_datetime = datetime.strptime(event_str, "%m/%d %I:%M %p")
        
        # Return the event datetime object in UTC timezone
        return pytz.utc.localize(event_datetime)
    except ValueError:
        return None

# Create event command     still have to fix the error
@bot.tree.command(name="create", description="Create a new event with title, time, and other details.")
async def create_event(interaction: discord.Interaction, 
                       title: str, 
                       event_date: str, 
                       event_time: str, 
                       description: str, 
                       duration: str = "1h", 
                       channel: discord.TextChannel = None, 
                       image: str = None, 
                       on_create_mention: str = None, 
                       on_start_mention: str = None):
    """Creates a new event with title, date, time, description, and other details."""

    # Defer the response to avoid interaction expiration
    await interaction.response.defer()

    # Parse the event datetime
    event_datetime = parse_event_datetime(event_date, event_time)
    if not event_datetime:
        return await interaction.followup.send("❌ Invalid date or time format! Use 'MM/DD' for date and 'X:XX AM/PM' for time.", ephemeral=True)

    # Convert event time to UTC
    event_datetime_utc = event_datetime.astimezone(pytz.utc)

    # Parse the duration
    duration_seconds = parse_duration(duration)
    if duration_seconds is None:
        return await interaction.followup.send("❌ Invalid duration format! Use '1h', '30min', '1 day', etc.", ephemeral=True)

    # Default channel to current if not specified
    if not channel:
        channel = interaction.channel

    # Create the embed message
    embed = discord.Embed(
        title=f"📆 {title}",
        description=description,
        color=discord.Color.blue(),
        timestamp=event_datetime_utc
    )

    embed.add_field(name="Time", value=f"{event_datetime_utc.strftime('%A, %B %d, %Y %I:%M %p UTC')}", inline=False)
    embed.add_field(name="Duration", value=duration, inline=False)
    embed.add_field(name="Attendees", value="0", inline=False)
    embed.add_field(name="Absentees", value="0", inline=False)

    if on_create_mention:
        embed.add_field(name="Created By", value=f"<@{on_create_mention}>", inline=False)
    if on_start_mention:
        embed.add_field(name="Starting Soon Mention", value=f"<@{on_start_mention}>", inline=False)

    if image:
        embed.set_image(url=image)

    # Send the event message
    message = await channel.send(embed=embed)
    await message.add_reaction("✅")  # Attendee reaction
    await message.add_reaction("❌")  # Absentee reaction

    # Store the event details
    event_data = {
        "title": title,
        "description": description,
        "event_time": event_datetime_utc,
        "duration": duration,
        "channel_id": channel.id,
        "image": image,
        "on_create_mention": on_create_mention,
        "on_start_mention": on_start_mention,
        "attendees": [],  # List of user IDs of attendees
        "absentees": [],  # List of user IDs of absentees
        "message_id": message.id,
    }

    # Store event info in the dictionary
    events[message.id] = event_data

    await interaction.followup.send("✅ Event created successfully!", ephemeral=True)

# Helper Function: Parse duration (e.g., '1h', '30min', '1 day')
def parse_duration(duration: str):
    """Parse duration (e.g., '1h', '30min', '1 day') to seconds."""
    duration = duration.lower()
    if duration.endswith("h"):  # Hours
        try:
            return int(duration[:-1]) * 3600
        except ValueError:
            return None
    elif duration.endswith("min"):  # Minutes
        try:
            return int(duration[:-3]) * 60
        except ValueError:
            return None
    elif duration.endswith("day"):  # Days
        try:
            return int(duration[:-3]) * 86400
        except ValueError:
            return None
    return None

# Reaction Event Listener: Handling reactions
@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    """Handles reactions to event messages (✅ or ❌)."""
    # Ensure the reaction is on an event message
    event_message = await reaction.message.channel.fetch_message(reaction.message.id)
    event_data = events.get(event_message.id)
    
    if not event_data:
        return

    if reaction.emoji == "✅":  # User wants to attend
        if user.id not in event_data["attendees"]:
            event_data["attendees"].append(user.id)
            # Update embed field for attendees count
            await update_event_embed(event_message, event_data)

            # Add user to attendees section
            embed = event_message.embeds[0]
            embed.set_field_at(2, name="Attendees", value=f"{len(event_data['attendees'])}", inline=False)
            embed.add_field(name="Attendees", value=f"<@{user.id}>", inline=False)
            await event_message.edit(embed=embed)

            await reaction.message.channel.send(f"{user.mention} has joined the event! 🎉")

            # Send a confirmation message in embed form
            confirmation_embed = discord.Embed(
                title="Confirmed",
                description="You must allow DMs from Sesh to set reminders.",
                color=discord.Color.green(),
            )
            confirmation_embed.set_thumbnail(url=bot.user.avatar.url)  # Set the bot as the thumbnail
            await user.send(embed=confirmation_embed)

    elif reaction.emoji == "❌":  # User will not attend
        if user.id not in event_data["absentees"]:
            event_data["absentees"].append(user.id)
            # Update embed field for absentee count
            await update_event_embed(event_message, event_data)

            # Add user to absentees section
            embed = event_message.embeds[0]
            embed.set_field_at(3, name="Absentees", value=f"{len(event_data['absentees'])}", inline=False)
            embed.add_field(name="Absentees", value=f"<@{user.id}>", inline=False)
            await event_message.edit(embed=embed)

            await reaction.message.channel.send(f"{user.mention} will not attend the event. 😞")

# Function to update the event embed with the latest attendees and absentees count
async def update_event_embed(message: discord.Message, event_data):
    """Update the event embed with the latest attendees and absentees count."""
    embed = message.embeds[0]
    
    attendees_count = len(event_data["attendees"])
    absentees_count = len(event_data["absentees"])

    # Update the attendees and absentees count
    embed.set_field_at(2, name="Attendees", value=f"{attendees_count}", inline=False)
    embed.set_field_at(3, name="Absentees", value=f"{absentees_count}", inline=False)

    # Update the embed message
    await message.edit(embed=embed)

# Reaction Event Listener: Handling reaction removal
@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.User):
    """Handles reaction removal (✅ or ❌)."""
    event_message = await reaction.message.channel.fetch_message(reaction.message.id)
    event_data = events.get(event_message.id)

    if not event_data:
        return

    if reaction.emoji == "✅":  # User is removing ✅
        if user.id in event_data["attendees"]:
            event_data["attendees"].remove(user.id)
            await update_event_embed(event_message, event_data)
            
            # Remove user from attendees section
            embed = event_message.embeds[0]
            attendees_field = embed.fields[2]
            attendees_list = [f"<@{user.id}>" for user in event_data["attendees"]]
            embed.set_field_at(2, name="Attendees", value=f"{len(event_data['attendees'])}\n" + "\n".join(attendees_list), inline=False)
            await event_message.edit(embed=embed)
            
            await reaction.message.channel.send(f"{user.mention} removed from the attendees list. 😞")

    elif reaction.emoji == "❌":  # User is removing ❌
        if user.id in event_data["absentees"]:
            event_data["absentees"].remove(user.id)
            await update_event_embed(event_message, event_data)
            
            # Remove user from absentees section
            embed = event_message.embeds[0]
            absentees_field = embed.fields[3]
            absentees_list = [f"<@{user.id}>" for user in event_data["absentees"]]
            embed.set_field_at(3, name="Absentees", value=f"{len(event_data['absentees'])}\n" + "\n".join(absentees_list), inline=False)
            await event_message.edit(embed=embed)
            
            await reaction.message.channel.send(f"{user.mention} removed from the absentees list. 😞")



 
bot.run(config.DISCORD_TOKEN) 