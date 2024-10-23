""" 
Sad attempt at making a betting thingy.
"""
import json
import os
import sys
from disnake.ext import commands
import disnake
from helpers import checks

# Ensure 'config.json' exists and load config values
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

GUILDID = int(config["GUILD_ID"])

# Define the path to the JSON files
USER_DATA_FILE = "user_data.json"
BET_DATA_FILE = "bet_data.json"
LEADERBOARD_FILE = "leaderboard.json"

def ensure_files_exist():
    """Ensure that the necessary files exist, creating them if they do not."""
    files = [USER_DATA_FILE, BET_DATA_FILE, LEADERBOARD_FILE]
    
    for file in files:
        if not os.path.isfile(file):
            with open(file, "w") as f:
                json.dump({}, f, indent=4)

def save_bet_data(bet_data):
    with open(BET_DATA_FILE, "w") as file:
        json.dump(bet_data, file, indent=4)

def load_bet_data():
    ensure_files_exist()
    try:
        with open(BET_DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def active_bet_exists():
    bet_data = load_bet_data()
    return "active_bet" in bet_data and bet_data["active_bet"]

def store_bet_data(user_id, amount=None, team=None):
    ensure_files_exist()
    try:
        with open(BET_DATA_FILE, "r") as file:
            bet_data = json.load(file)
    except FileNotFoundError:
        bet_data = {}

    if "active_bet" not in bet_data or not bet_data["active_bet"]:
        bet_data["active_bet"] = {"bets": {}, "user_id": user_id, "start_bets": []}

    if amount is not None:
        bet_data["active_bet"]["initial_amount"] = amount
        bet_data["active_bet"]["start_bets"].append(user_id)

    if team:
        bet_data["active_bet"]["bets"][user_id] = {
            "amount": int(amount),  # Ensure the amount is stored as an integer
            "team": team
        }

    with open(BET_DATA_FILE, "w") as file:
        json.dump(bet_data, file, indent=4)


def load_user_data():
    ensure_files_exist()
    try:
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(user_data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

def add_user(user_id):
    user_data = load_user_data()
    if user_id not in user_data:
        user_data[user_id] = {"balance": 200}  # Start with 200
        save_user_data(user_data)
        return True
    return False

def calculate_winnings(result, bet_data, odds):
    total_bet_on_result = sum(
        bet_info["amount"]
        for bet_info in bet_data["active_bet"]["bets"].values()
        if bet_info["team"] == result
    )
    
    if total_bet_on_result == 0:
        return {}  # No winnings if no bets on the result

    user_winnings = {}
    for user_id, bet_info in bet_data["active_bet"]["bets"].items():
        if bet_info["team"] == result:
            winnings = int(bet_info["amount"] * odds[result])
            user_winnings[user_id] = winnings

    return user_winnings

def update_leaderboard():
    user_data = load_user_data()
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

def get_leaderboard():
    ensure_files_exist()
    with open(LEADERBOARD_FILE, "r") as file:
        return json.load(file)

class Betting(commands.Cog, name='Betting'):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="bet_help",
        description="Display information about all betting commands."
    )
    @checks.not_blacklisted()
    async def bet_help(self, interaction: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="Betting Commands Help 📖",
            description="Here are the commands you can use for betting:",
            color=disnake.Color.blue()
        )

        commands_info = {
            "/bet_register": "Register as a user for betting.",
            "/bet_start": "Start a new bet.",
            "/bet_placebet": "Place a bet on either Team Uno or Team Dos.\n"
                             "  - amount: The amount of money to bet.\n"
                             "  - team: The team to bet on (Team Uno or Team Dos).",
            "/bet_endbet": "End the active bet and declare the winning team.\n"
                           "  - winner: The winning team (Team Uno or Team Dos).",
            "/bet_balance": "Check your current balance.",
            "/bet_history": "View your betting history.",
            "/bet_recharge": "Recharge your € if you are out of money.",
            "/bet_leaderboard": "View the top users based on €.",
            "/bet_stats": "View statistics about current and past bets."
        }

        for command, description in commands_info.items():
            embed.add_field(name=command, value=description, inline=False)

        embed.set_footer(text="Use these commands to participate in betting and manage your bets. Good luck!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="bet_register",
        description="Register as a user for betting."
    )
    async def register_user(self, interaction: disnake.ApplicationCommandInteraction):
        user_id = str(interaction.author.id)
        if add_user(user_id):
            embed = disnake.Embed(
                title="Registration Complete ✅",
                description="You have been successfully registered for betting! 🎉",
                color=disnake.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(
                title="Already Registered 🔄",
                description="You are already registered for betting. No need to register again!",
                color=disnake.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="bet_start",
        description="Start a new bet."
    )
    @checks.not_blacklisted()
    async def start_bet(self, interaction: disnake.ApplicationCommandInteraction):
        if active_bet_exists():
            embed = disnake.Embed(
                title="Bet Already Active ⏳",
                description="There is already an active bet. Please wait until it ends before starting a new one.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        user_id = str(interaction.author.id)
        store_bet_data(user_id)
        embed = disnake.Embed(
            title="New Bet Started 🚀",
            description=f"A new bet has been started by {interaction.author.display_name}. Get ready to place your bets! 🎲",
            color=disnake.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="bet_placebet",
        description="Place a bet on either Team Uno, Team Dos, or Draw.",
        options=[
            disnake.Option(
                name="amount",
                description="The amount of money to bet.",
                type=disnake.OptionType.integer,
                required=True
            ),
            disnake.Option(
                name="team",
                description="The team or draw to bet on.",
                type=disnake.OptionType.string,
                required=True,
                choices=[
                    disnake.OptionChoice("Team Uno", "Team Uno"),
                    disnake.OptionChoice("Team Dos", "Team Dos"),
                    disnake.OptionChoice("Draw", "Draw")
                ]
            )
        ]
    )
    @checks.not_blacklisted()
    async def place_bet(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        amount: int,
        team: str
    ):
        user_id = str(interaction.author.id)
        user_data = load_user_data()

        if user_id not in user_data:
            embed = disnake.Embed(
                title="Not Registered ❌",
                description="You are not registered for betting. Please register using /bet_register.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user_data[user_id]["balance"] < amount:
            embed = disnake.Embed(
                title="Insufficient Balance 💸",
                description="You do not have enough balance to place this bet.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not active_bet_exists():
            embed = disnake.Embed(
                title="No Active Bet ⏳",
                description="There is no active bet at the moment. Please wait until a new bet starts.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        store_bet_data(user_id, amount, team)
        user_data[user_id]["balance"] -= amount
        save_user_data(user_data)

        embed = disnake.Embed(
            title="Bet Placed Successfully ✅",
            description=f"You have placed a bet of {amount} on {team}. Good luck! 🍀",
            color=disnake.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="bet_endbet",
        description="End the active bet and declare the winning team or draw.",
        options=[
            disnake.Option(
                name="winner",
                description="The winning team or draw.",
                type=disnake.OptionType.string,
                required=True,
                choices=[
                    disnake.OptionChoice("Team Uno", "Team Uno"),
                    disnake.OptionChoice("Team Dos", "Team Dos"),
                    disnake.OptionChoice("Draw", "Draw")
                ]
            )
        ]
    )
    @checks.not_blacklisted()
    async def end_bet(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        winner: str
    ):
        if not active_bet_exists():
            embed = disnake.Embed(
                title="No Active Bet ⏳",
                description="There is no active bet to end.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        user_id = str(interaction.author.id)
        bet_data = load_bet_data()

        if bet_data["active_bet"]["user_id"] != user_id:
            embed = disnake.Embed(
                title="Not Authorized ❌",
                description="You are not authorized to end this bet.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Calculate odds based on current bets
        total_bets = sum(bet_info["amount"] for bet_info in bet_data["active_bet"]["bets"].values())
        odds = {}
        for team in ['Team Uno', 'Team Dos', 'Draw']:
            total_bet_on_team = sum(bet_info["amount"] for bet_info in bet_data["active_bet"]["bets"].values() if bet_info["team"] == team)
            odds[team] = total_bets / (total_bet_on_team if total_bet_on_team > 0 else 1)

        winnings = calculate_winnings(winner, bet_data, odds)
        user_data = load_user_data()

        if winnings:
            winners_message = ""
            for user_id, amount in winnings.items():
                user_data[user_id]["balance"] += amount
                member = interaction.guild.get_member(int(user_id))
                if member is None:
                    member = await interaction.guild.fetch_member(int(user_id))
                winners_message += f"{member.display_name}: {amount} €\n"

            embed = disnake.Embed(
                title="Bet Ended 🏁",
                description=f"The bet has ended! The result is {winner}.\nCongratulations to the winners! 🎉\n\nWinners and their winnings:\n{winners_message}",
                color=disnake.Color.green()
            )
        else:
            embed = disnake.Embed(
                title="Bet Ended 🏁",
                description=f"The bet has ended!\nThe result is {winner}.\nUnfortunately, there were no winners this time.",
                color=disnake.Color.red()
            )

        bet_data["active_bet"] = None
        save_bet_data(bet_data)
        save_user_data(user_data)
        update_leaderboard()

        await interaction.response.send_message(embed=embed)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="bet_balance",
        description="Check your current balance."
    )
    @checks.not_blacklisted()
    async def balance(self, interaction: disnake.ApplicationCommandInteraction):
        user_id = str(interaction.author.id)
        user_data = load_user_data()

        if user_id not in user_data:
            embed = disnake.Embed(
                title="Not Registered 🛑",
                description="You need to register to check your balance. Use the /register command.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if user_data[user_id]["balance"] == 0:
            embed = disnake.Embed(
                title="No Funds 💸",
                description="You don't have any funds. Recharge your balance with the `/recharge` command.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        balance = user_data[user_id]["balance"]
        embed = disnake.Embed(
            title="Current Balance 💰",
            description=f"Your current balance is **{balance}** €.\nKeep betting or save it up! 😉",
            color=disnake.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="bet_history",
        description="View your betting history."
    )
    @checks.not_blacklisted()
    async def history(self, interaction: disnake.ApplicationCommandInteraction):
        user_id = str(interaction.author.id)
        bet_data = load_bet_data()

        if "bets" in bet_data["active_bet"] and user_id in bet_data["active_bet"]["bets"]:
            bet_info = bet_data["active_bet"]["bets"][user_id]
            amount = bet_info["amount"]
            team = bet_info["team"]
            await interaction.response.send_message(f"You bet {amount} on {team}.", ephemeral=True)
        else:
            await interaction.response.send_message("You have not placed any bets or there are no active bets.", ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="bet_recharge",
        description="Recharge your € if you are out of money."
    )
    @checks.not_blacklisted()
    async def recharge(self, interaction: disnake.ApplicationCommandInteraction):
        user_id = str(interaction.author.id)
        
        # Load user data
        user_data = load_user_data()
    
        # Check if user is registered
        if user_id not in user_data:
            await interaction.response.send_message("You need to register first.", ephemeral=True)
            return
    
        # Check balance and recharge if needed
        if user_data[user_id]["balance"] <= 0:
            user_data[user_id]["balance"] = 50  # Set balance to default
            save_user_data(user_data)  # Save updated user data
            
            # Confirm recharge
            await interaction.response.send_message("Your money has been recharged to 50 €.", ephemeral=True)
        else:
            await interaction.response.send_message("You still have money left. No recharge needed.", ephemeral=True)

    @commands.slash_command(
            guild_ids=[GUILDID],
            name="bet_leaderboard",
            description="View the top users based on €."
    )
    @checks.not_blacklisted()
    async def leaderboard(self, interaction: disnake.ApplicationCommandInteraction):
        user_data = get_leaderboard()
        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['balance'], reverse=True)
        leaderboard_message = "Leaderboard:\n"
        for user_id, data in sorted_users[:5]:  # Show top 5
            member = interaction.guild.get_member(int(user_id))
            if member is None:
                member = await interaction.guild.fetch_member(int(user_id))
            leaderboard_message += f"{member.display_name}: {data['balance']} €\n"

        embed = disnake.Embed(title="Leaderboard 🏅", description=leaderboard_message, color=disnake.Color.blue())
        await interaction.response.send_message(embed=embed) # , ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="bet_stats",
        description="View statistics about current and past bets."
    )
    @checks.not_blacklisted()
    async def bet_stats(self, interaction: disnake.ApplicationCommandInteraction):
        bet_data = load_bet_data()
        active_bet = bet_data.get("active_bet")

        if not active_bet:
            embed = disnake.Embed(
                title="No Active Bet Stats 📉",
                description="There are no active bet stats to display.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Calculate odds based on current bets
        total_bets = sum(bet_info['amount'] for bet_info in active_bet['bets'].values())
        odds = {}
        for team in ['Team Uno', 'Team Dos', 'Draw']:
            total_bet_on_team = sum(bet_info['amount'] for bet_info in active_bet['bets'].values() if bet_info['team'] == team)
            odds[team] = total_bets / (total_bet_on_team if total_bet_on_team > 0 else 1)

        # Calculate total bets per option
        bet_totals = {
            'Team Uno': sum(bet_info['amount'] for bet_info in active_bet['bets'].values() if bet_info['team'] == 'Team Uno'),
            'Team Dos': sum(bet_info['amount'] for bet_info in active_bet['bets'].values() if bet_info['team'] == 'Team Dos'),
            'Draw': sum(bet_info['amount'] for bet_info in active_bet['bets'].values() if bet_info['team'] == 'Draw')
        }

        embed = disnake.Embed(
            title="Active Bet Stats 📈",
            description=f"Current odds:\n"
                        f"Team Uno: {odds.get('Team Uno', 'N/A'):.2f}\n"
                        f"Team Dos: {odds.get('Team Dos', 'N/A'):.2f}\n"
                        f"Draw: {odds.get('Draw', 'N/A'):.2f}\n\n"
                        f"Bet Amounts:\n"
                        f"Team Uno: {bet_totals['Team Uno']}\n"
                        f"Team Dos: {bet_totals['Team Dos']}\n"
                        f"Draw: {bet_totals['Draw']}",
            color=disnake.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

def setup(bot):
    ensure_files_exist()  # Ensure the files exist when setting up the bot
    bot.add_cog(Betting(bot))

