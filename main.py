from discord import Intents, Embed, Status, Game, Member, File  # type: ignore
from discord.ext.commands import Bot, errors, has_permissions  # type: ignore
from discord.ext import tasks  # type: ignore
from discord.utils import get  # type: ignore
import json
import datetime
from dotenv import load_dotenv  # type: ignore
import os  # type: ignore
from PIL import Image, ImageDraw, ImageFont  # type: ignore

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ROUTINE_TIME = datetime.time(14, 45, 0)
ROUTINE_CONFIRM = datetime.time(14, 15, 0)

updated_d = {}
updated_c = {}

intents: Intents = Intents.default()
intents.message_content = True
intents.members = True
Client = Bot(command_prefix="!", intents=intents, help_command=None)

async def daily_test_update() -> None:
    try:
        with open("test.json", "r") as file:
            data = json.load(file)
        tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        if tomorrow in data:
            for test in data[tomorrow]:
                await Client.get_channel(1208009536565420052).send(f"Test: {test} tomorrow")
    except Exception as e:
        print(e)
    

async def add_test_function(date: str, test: str) -> None:
    try:
        with open("test.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    
    if date in data:
        data[date].append(test)
    else:
        data[date] = [test]
    with open("test.json", "w") as file:
        json.dump(data, file)

async def remove_test_function(date: str, test: str) -> None:
    try:
        with open("test.json", "r") as file:
            data = json.load(file)
        with open("test.json", "w") as file:
            if date in data:
                data[date].remove(test)
                if data[date] == []:
                    data.pop(date)
                json.dump(data, file)
            else:
                return
    except Exception as e:
        print(e)

async def get_test_function() -> str:
    try:
        with open("test.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data


async def AddAssignment(subject: str, date: str, assignment: str) -> None:
    try:
        with open("assignments.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    if date in data:
        data[date].append(f"{subject}: {assignment}")
    else:
        data[date] = [f"{subject}: {assignment}"]
    with open("assignments.json", "w") as file:
        json.dump(data, file)


async def RemoveAssignment(date: str, subject: str, assignment: str) -> None:
    with open("assignments.json", "r") as file:
        data = json.load(file)
    with open("assignments.json", "w") as file:
        if date in data:
            data[date].remove(f"{subject}: {assignment}")
            print(data[date])
            if data[date] == []:
                data.pop(date)
            json.dump(data, file)
        else:
            return


async def GetAssignments() -> str:
    try:
        with open("assignments.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data


async def routine_image(group: str) -> None:
    try:
        day = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%A")
        day = day.lower()
        day = day.capitalize()
        date = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        data = await get_routine(group)
        img = Image.open(f"Routine_{group.upper()}.png")
        if data[day] == {}:
            img.save(f"./routine{group.lower()}.png")
        d = ImageDraw.Draw(img)
        fnt = ImageFont.truetype("Arial.ttf", 30)
        d.text((124, 90), f"{date}", fill=(255, 255, 255), font=fnt)
        d.text((319, 90), f"{day}", fill=(255, 255, 255), font=fnt)
        fnt = ImageFont.truetype("Arial.ttf", 25)
        for i, items in enumerate(data[day]):
            items = items.split(",")
            d.text(
                (31, 120 + (i + 1) * 50),
                f"{items[0]}: {items[1]}",
                fill=(255, 255, 255),
                font=fnt,
            )
        img.save(f"./routine{group.lower()}.png")
    except Exception as e:
        print(e)


async def AddEvent(date: str, event: str) -> None:
    with open("events.json", "r") as file:
        data = json.load(file)
    if date in data:
        data[date].append(event)
    else:
        data[date] = [event]
    with open("events.json", "w") as file:
        json.dump(data, file)


async def RemoveEvent(date: str, event: str) -> None:
    with open("events.json", "r") as file:
        data = json.load(file)
    with open("events.json", "w") as file:
        if date in data:
            data[date].remove(event)
            if data[date] == []:
                data.pop(date)
            json.dump(data, file)
        else:
            return


async def assignment_image(assignments) -> None:
    try:
        img = Image.open("assignments.png")
        d = ImageDraw.Draw(img)
        d.rectangle([(44, 96), (img.width, img.height)], fill=(0, 0, 0))
        fnt1 = ImageFont.truetype("Arial.ttf", 35)
        fnt2 = ImageFont.truetype("Arial.ttf", 25)
        for i, (teacher, value) in enumerate(assignments.items()):
            d.text((44, 85 + i * 50), f"{teacher}", fill=(0, 255, 0), font=fnt1)
            for j, assignment in enumerate(value):
                date = assignment.split(":")[0]
                subject = assignment.split(":")[1]
                day = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A")
                d.text(
                    (44, 125 + i * 50 + j * 50),
                    f"{j + 1}. {date}({day}) - {subject}",
                    fill=(255, 255, 255),
                    font=fnt2,
                )
        img.save("assignment.png")
    except Exception as e:
        print(e)


async def event_image(events) -> None:
    try:
        img = Image.open("events.png")
        d = ImageDraw.Draw(img)
        d.rectangle([(44, 96), (img.width, img.height)], fill=(0, 0, 0))
        fnt = ImageFont.truetype("Arial.ttf", 35)
        for i, (date, value) in enumerate(events.items()):
            day = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A")
            d.text((44, 85 + i * 50), f"{date} ({day})", fill=(0, 255, 0), font=fnt)
            for j, event in enumerate(value):
                d.text(
                    (44, 125 + i * 50 + j * 50),
                    f"{j + 1}. {event}",
                    fill=(255, 255, 255),
                    font=fnt,
                )
        img.save("event.png")
    except Exception as e:
        print(e)


async def get_routine(group: str) -> str:
    global updated_d, updated_c
    if group.lower() == "d":
        if updated_d != {}:
            return updated_d
    elif group.lower() == "c":
        if updated_c != {}:
            return updated_c

    with open(f"Routine_{group.lower()}.json", "r") as file:
        routine = json.load(file)
    return routine


async def get_members(guild_id: int) -> str:
    try:
        guild = Client.get_guild(guild_id)
        members = guild.members
        return members
    except Exception as e:
        print(e)
        return None

async def test_image(channel:str):
    try:
        img = Image.new("RGB", (500, 800), color=(0, 0, 0))
        d = ImageDraw.Draw(img)
        fnt1 = ImageFont.truetype("Arial.ttf", 45)
        d.text((180, 13), "Tests", fill=(255, 255, 255), font=fnt1, stroke_fill='white')
        d.line([(180, 60), (300,60)], fill=(255, 255, 255), width=4)
        fnt = ImageFont.truetype("Arial.ttf", 35)
        fnt2 = ImageFont.truetype("Arial.ttf", 25)
        with open("test.json", "r") as file:
            data = json.load(file)
        for i, (date, value) in enumerate(data.items()):
            day = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A")
            d.text((44, 85 + i * 85), f"{date}({day})", fill=(0, 255, 0), font=fnt)
            for j, test in enumerate(value):
                d.text(
                    (44, 135 + i * 80 + j * 80),
                    f"{j + 1}. {test}",
                    fill=(255, 255, 255),
                    font=fnt2,
                )
        img.save("test.png")
    except Exception as e:
        print(e)


@tasks.loop(time=ROUTINE_TIME)
async def send_routine() -> None:
    try:
        channel = await Client.fetch_channel(1208790747537604618)
        global updated_d, updated_c
        await routineimage(channel, "c")
        await routineimage(channel, "d")
        updated_d = {}
        updated_c = {}
        await daily_test_update()
    except Exception as e:
        print(e)


@Client.event
async def on_command_error(ctx, error) -> None:
    if isinstance(error, errors.CommandNotFound):
        await ctx.send("Command not found")
    elif isinstance(error, errors.MissingPermissions):
        await ctx.send("Missing required permission")
    else:
        print(error)


@Client.event
async def on_ready() -> None:
    await Client.change_presence(status=Status.idle, activity=Game("!help"))
    send_routine.start()
    send_routine_confirm.start()
    print(f"{Client.user} has connected to Discord!")


@tasks.loop(time=ROUTINE_CONFIRM)
async def send_routine_confirm() -> None:
    try:
        channel = await Client.fetch_channel(1208958358217039903)
        await channel.send(
            "Routine will be sent at 8:00 PM. Please confirm the routine "
        )
        await routineimage(channel, "c")
        await routineimage(channel, "d")
    except Exception as e:
        print(e)

@Client.command()
@has_permissions(administrator=True)
async def add_test(ctx, date: str, test: str) -> None:
    try:
        await add_test_function(date, test)
        await ctx.send(f"{test} has been added to {date}")
    except Exception as e:
        print(e)

@Client.command()
@has_permissions(administrator=True)
async def remove_test(ctx, date: str, test: str) -> None:
    try:
        await remove_test_function(date, test)
        await ctx.send(f"{test} has been removed from {date}")
    except Exception as e:
        print(e)
    
@Client.command()
async def get_test(ctx) -> None:
    try:
        tests = await get_test_function()
        if tests == {}:
            await ctx.send("No tests available")
            return
        await test_image(ctx)
        await ctx.send(file=File("test.png"))
    except Exception as e:
        print(e)

@Client.command()
async def routineimage(ctx, group: str) -> None:
    try:
        await routine_image(group)
        with open("events.json", "r") as file:
            try:
                events = json.load(file)
            except:
                events = {}
        day = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%A")
        date = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        if not date in events.keys():
            pass
        elif "Holiday" in events[date]:
            await ctx.send(f"{day} is a holiday")
            return
        await ctx.send(file=File(f"./routine{group.lower()}.png"))
    except Exception as e:
        print(e)


@Client.command()
@has_permissions(administrator=True)
async def add_assignment(ctx, subject: str, date: str, assignment: str) -> None:
    try:
        await AddAssignment(subject, date, assignment)
        await ctx.send(f"{assignment} has been added to {date}")
    except Exception as e:
        print(e)


@Client.command()
@has_permissions(administrator=True)
async def remove_assignment(ctx, date: str, subject: str, assignment: str) -> None:
    try:
        await RemoveAssignment(date, subject, assignment)
        await ctx.send(f"{assignment} has been removed from {date}")
    except Exception as e:
        print(e)


@Client.command()
async def get_assignments(ctx) -> None:
    try:
        assignments = await GetAssignments()
        if assignments == {}:
            await ctx.send("No assignments available")
            return
        await assignment_image(assignments)
        await ctx.send(file=File("assignment.png"))
    except Exception as e:
        print(e)


@Client.command()
@has_permissions(administrator=True)
async def update_routine(ctx, group: str, *, message: str) -> None:
    try:
        day = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%A")
        global updated_d, updated_c
        routine = {}
        if group.lower() == "d":
            if updated_d != {}:
                routine = updated_d
            else:
                with open(f"Routine_d.json", "r") as file:
                    routine = json.load(file)
        elif group.lower() == "c":
            if updated_c != {}:
                routine = updated_c
            else:
                with open(f"Routine_c.json", "r") as file:
                    routine = json.load(file)

        for i, teacher in enumerate(routine[day]):
            if message.split(",")[0] in teacher:
                routine[day][i] = message
                break
        else:
            routine[day].append(message)
        if group.lower() == "d":
            updated_d = routine
        elif group.lower() == "c":
            updated_c = routine
        await ctx.send(f"{message} has been updated.")
    except Exception as e:
        print(e)


@Client.command()
async def verify(ctx, roll_no, member: Member = None) -> None:
    try:
        if member is None:
            member = ctx.message.author

        with open("students.json", "r") as file:
            students = json.load(file)

        if roll_no in students:
            if students[roll_no][1] == "True":
                await ctx.send("Already verified.")
                return
            role = get(
                ctx.guild.roles, name="Group C" if int(roll_no[-3:]) < 73 else "Group D"
            )
            await member.remove_roles(get(ctx.guild.roles, name="Group C"))
            await member.remove_roles(get(ctx.guild.roles, name="Group D"))
            await member.add_roles(role)
            await member.edit(nick=students[roll_no][0].lower().capitalize())
            await ctx.send(f"{member.display_name} has been verified.")

            with open("students.json", "r") as file:
                data = json.load(file)
            data[roll_no][1] = "True"
            with open("students.json", "w") as file:
                json.dump(data, file)
        else:
            await ctx.send("Invalid roll number. Would you like to be Guest?(!guest)")
    except Exception as e:
        print(e)


@Client.command()
@has_permissions(administrator=True)
async def verify_admin(ctx) -> None:
    members = await get_members(ctx.message.guild.id)
    channel = await Client.fetch_channel(1195990712278327347)

    with open("students.json", "r") as file:
        students = json.load(file)
    for member in members:
        if not member.bot:
            try:
                if any(
                    role in ["Seniors", "Guest"]
                    for role in [role.name for role in member.roles]
                ):
                    continue
                name = member.display_name.upper()
                name_list = [name[0] for name in students.values()]
                if name not in name_list:
                    await channel.send(f"{member.display_name} is not verified.")
                else:
                    index = name_list.index(name)
                    await member.edit(nick=name.lower().capitalize())
                    await verify(ctx, roll_no=students.keys()[index])
            except Exception as e:
                print(e)


@Client.command()
async def guest(ctx) -> None:
    try:
        member = ctx.message.author
        role = get(ctx.guild.roles, name="Guest")
        await member.add_roles(role)
        await ctx.send(f"{member.name} has been verified as Guest.")
    except Exception as e:
        print(e)


@Client.command()
async def routine(ctx, group: str) -> None:
    try:
        await routineimage(ctx, group)
    except Exception as e:
        print(e)


@Client.command()
async def help(ctx) -> None:
    await ctx.send("Help command banauna alchi lagyo :)")


@Client.command()
@has_permissions(administrator=True)
async def add_event(ctx, date: str, event: str) -> None:
    try:
        await AddEvent(date, event)
        await ctx.send(f"{event} has been added to {date}")
    except Exception as e:
        print(e)


@Client.command()
@has_permissions(administrator=True)
async def remove_event(ctx, date: str, event: str) -> None:
    try:
        await RemoveEvent(date, event)
        await ctx.send(f"{event} has been removed from {date}")
    except Exception as e:
        print(e)


@Client.command()
async def get_events(ctx) -> None:
    try:
        with open("events.json", "r") as file:
            try:
                events = json.load(file)
            except:
                events = {}
        if events == {}:
            await ctx.send("No events available")
            return
        await event_image(events)
        await ctx.send(file=File("event.png"))
    except Exception as e:
        print(e)


def main() -> None:
    Client.run(TOKEN)


if __name__ == "__main__":

    main()
