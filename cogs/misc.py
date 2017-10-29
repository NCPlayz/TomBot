from os import listdir, environ
import discord
from bs4 import BeautifulSoup
from discord.ext.commands import command, group
from utils.connectors import fetch
from random import randint, choice, sample
from enum import Enum
from io import BytesIO
import aiohttp
import asyncio
import datetime


FULLWIDTH_OFFSET = 65248


class RPS(Enum):
    rock = "\N{MOYAI}"
    paper = "\N{PAGE FACING UP}"
    scissors = "\N{BLACK SCISSORS}"


class RPSParser:
    def __init__(self, argument):
        argument = argument.lower()
        if argument == "rock":
            self.choice = RPS.rock
        elif argument == "paper":
            self.choice = RPS.paper
        elif argument == "scissors":
            self.choice = RPS.scissors
        else:
            return


class Misc:
    """Quote commands."""
    def __init__(self, bot):
        self.bot = bot
        self._weather_key = environ['WEATHER']
        self._nasa_key = environ['NASA']

    @command(aliases=['fw', 'fullwidth', 'ａｅｓｔｈｅｔｉｃ'], usage='<msg>')
    async def aesthetic(self, ctx, *, msg="aesthetic"):
        """ａｅｓｔｈｅｔｉｃ."""
        await ctx.send("".join(map(
            lambda c: chr(ord(c) + FULLWIDTH_OFFSET) if (ord(c) >= 0x21 and ord(c) <= 0x7E) else c,
            msg)).replace(" ", chr(0x3000)))

    @command()
    async def clap(self, ctx, *, msg):
        msg = msg.replace(" ", "\U0001f44f")
        await ctx.send(msg)

    @command(aliases=["choose"])
    async def decide(self, ctx, *choices: str):
        """Decides between things for you."""
        await ctx.send(f"Obviously, the answer is {choice(choices)}.")

    @command(aliases=["element"])
    async def atom(self, ctx, element):
        """Displays information for a given atom"""
        try:
            html = await fetch(ctx.session, f"http://www.chemicalelements.com/elements/{element.lower()}.html", timeout=15,
                               return_type='text')
        except:
            await ctx.send(f"Could not find and element with the symbol \"{element.upper()}\"")
            return
        soup = BeautifulSoup(html, "html.parser")

        text = soup.get_text()

        element_name = text.split('Name: ')[1].split('\n')[0]
        element_symbol = text.split('Symbol: ')[1].split('\n')[0]
        atomic_number = text.split('Atomic Number: ')[1].split('\n')[0]
        atomic_mass = text.split('Atomic Mass: ')[1].split('\n')[0]
        neutrons = text.split('Number of Neutrons: ')[1].split('\n')[0]
        shells = text.split('Number of Energy Levels: ')[1].split('\n')[0]
        family = text.split('Classification: ')[1].split('\n')[0]
        color = text.split('Color: ')[1].split('\n')[0]
        uses = text.split('Uses: ')[1].split('\n')[0]
        discovery_year = text.split('Date of Discovery: ')[1].split('\n')[0]
        discoverer = text.split('Discoverer: ')[1].split('\n')[0]

        embed = discord.Embed(title=element_name, colour=0x33cc82, type="rich")
        embed.add_field(name='Name', value=element_name)
        embed.add_field(name='Symbol', value=element_symbol)
        embed.add_field(name='Atomic Number', value=atomic_number)
        embed.add_field(name='Atomic Mass', value=atomic_mass)
        embed.add_field(name='Neutrons', value=neutrons)
        embed.add_field(name='Shells', value=shells)
        embed.add_field(name='Family', value=family)
        embed.add_field(name='Color', value=color)
        embed.add_field(name='Uses', value=uses)
        embed.add_field(name='Year of Discovery', value=discovery_year)
        embed.add_field(name='Discoverer', value=discoverer)

        await ctx.send(embed=embed)

    @command(aliases=["tom_pic", "angorpic"])
    async def tompic(self, ctx):
        await ctx.send(content='\u200B', file=discord.File(f"./photos/{choice(listdir('./photos'))}"))

    @command()
    async def roll(self, ctx, number: int=100):
        """Rolls random number (between 1 and user choice)
        Defaults to 100."""
        if number > 1:
            await ctx.send(f"{ctx.author.mention} | :game_die: {randint(1, number)}")
        else:
            await ctx.send(f"{ctx.author.mention} Maybe higher than 1? :wink:")

    @command()
    async def flip(self, ctx, user: discord.Member=None):
        """Flips a coin... or a user.
        Defaults to coin.
        """
        if user is not None:
            msg = ""
            if user == ctx.bot.user:
                user = ctx.message.author
                msg = "Nice try. You think this is funny? How about *this* instead:\n\n"
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.display_name.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            await ctx.send(msg + "(╯°□°）╯︵ " + name[::-1])
        else:
            await ctx.send("*flips a coin and... " + choice(["HEADS!*", "TAILS!*"]))

    @command(pass_context=True)
    async def rps(self, ctx, your_choice: RPSParser):
        """Play rock paper scissors"""
        player_choice = your_choice.choice
        tb_choice = choice((RPS.rock, RPS.paper, RPS.scissors))
        cond = {
                (RPS.rock,     RPS.paper): False,
                (RPS.rock,     RPS.scissors): True,
                (RPS.paper,    RPS.rock): True,
                (RPS.paper,    RPS.scissors): False,
                (RPS.scissors, RPS.rock): False,
                (RPS.scissors, RPS.paper): True
               }

        if tb_choice == player_choice:
            outcome = None  # Tie
        else:
            outcome = cond[(player_choice, tb_choice)]

        if outcome is True:
            await ctx.send(f"{tb_choice.value} You win {ctx.author.mention}!")
        elif outcome is False:
            await ctx.send(f"{tb_choice.value} You lose {ctx.author.mention}!")
        else:
            await ctx.send("{tb_choice.value} We're square {ctx.author.mention}!")

    @command(aliases=["8ball"])
    async def ask(self, ctx, *, question=None):
        """Ask a question"""
        question = question.lower()

        if question.startswith("should"):
            responses = ("Yes", "No", "Definitely", "Sure", "Of course", "Maybe",
                         "Probably" "Definitely not", "No way", "Please don't",
                         "Go ahead!", "I mean, if you want to, sure", "Sure, but be careful",
                         "That's probably not a good idea")
        elif question.startswith("where"):
            fast_food_chains = ("McDonald's", "Wendy's", "Burger King", "A&W", "KFC", "Taco Bell")
            responses = ("Just over there", "In your closet", "Probably hiding from you",
                         f"At the nearest {choice(fast_food_chains)}",
                         "Right behind you", "At the store", "Just a few blocks away",
                         "Nowhere near here")
        elif question.startswith("when"):
            time_units = ("years", "months", "days", "hours", "minutes", "seconds")
            responses = ("In a few hours", "Sometime this month", "When pigs fly",
                         "Not anythime soon, that's for sure", "By the end of the week",
                         "Let's hope that never happens", "I am genuinely unsure",
                         "Soon", "No idea, but be sure to tell me when it does",
                         "In a dog's age", "I don't know, but hopefully it's in my lifetime",
                         f"In {randint(1, 101)} {choice(time_units)}")
        elif question.startswith("who"):
            html = await fetch(ctx.session, "https://www.randomlists.com/random-celebrities?a", timeout=15,
                               return_type='text')
            soup = BeautifulSoup(html, "html.parser")
            tags = soup.find_all(class_="crux")
            celebrities = []
            for tag in tags:
                celebrities.append(tag.text)
            responses = celebrities
        elif question.startswith(("what movie should", "what film should")):
            html = await fetch(ctx.session, "https://www.randomlists.com/random-movies?a", timeout=15,
                               return_type='text')
            soup = BeautifulSoup(html, "html.parser")
            tags = soup.find_all(class_="support")
            movies = []
            for tag in tags:
                movies.append(tag.text)
            responses = movies
        elif question.startswith(("what game should", "what video game should", "what videogame should")):
            html = await fetch(ctx.session, "https://www.randomlists.com/random-video-games?a", timeout=15,
                               return_type='text')
            soup = BeautifulSoup(html, "html.parser")
            tags = soup.find_all(class_="support")
            games = []
            for tag in tags:
                games.append(tag.text)
            responses = games
        else:
            responses = ("Yes", "No", "Definitely", "Sure", "Of course", "Maybe",
                         "Probably", "Most likely", "Definitely not", "No way",
                         "I hope not", "Better be", "I don't think so")

        if question is None:
            await ctx.send("You forgot to ask a question")
        else:
            await ctx.send(choice(responses))

    @command()
    async def lmgtfy(self, ctx, *, search_terms: str):
        """Creates a lmgtfy link"""
        await ctx.send(f"https://lmgtfy.com/?q={search_terms}")

    @command(hidden=True)
    async def hug(self, ctx, user: discord.Member=None, intensity: int=1):
        """Because everyone likes hugs
        Up to 10 intensity levels."""
        name = user.display_name or ctx.author.display_name
        msg = None
        if intensity <= 0:
            msg = "(っ˘̩╭╮˘̩)っ" + name
        elif intensity <= 3:
            msg = "(っ´▽｀)っ" + name
        elif intensity <= 6:
            msg = "╰(*´︶`*)╯" + name
        elif intensity <= 9:
            msg = "(つ≧▽≦)つ" + name
        elif intensity >= 10:
            msg = "(づ￣ ³￣)づ*{}* ⊂(´・ω・｀⊂)".format(name)
        await ctx.send(msg)

    @staticmethod
    async def bytes_download(ctx, url: str, file_ext: str):
        try:
            with ctx.session as session:
                with aiohttp.Timeout(5):
                    async with session.get(url) as resp:
                        data = await resp.read()
                        b = BytesIO(data)
                        b.seek(0)
                        return discord.File(fp=b, filename=f"Image.{file_ext}")
        except asyncio.TimeoutError:
            return False

    @command(aliases=["DAB", "damazingbutt"])
    async def dab(self, ctx):
        """Duncan's Amazing Butt"""
        await ctx.send(
            file=(await self.bytes_download(
                ctx,
                "https://media.discordapp.net/attachments/266593626501545984/348277117059989504/duncandab.png",
                "png"
            )))

    @command(aliases=["luna"])
    async def chip(self, ctx):
        """Luna!"""
        chip_list = ["https://cdn.discordapp.com/attachments/266593626501545984/350441525248786432/image.jpg",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350756351586074624/IMG_0108.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350756603764539412/IMG_0155.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350757778605735956/IMG_6496.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350757847535190036/IMG_7624.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350758204755410979/IMG_7696.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350758475460247563/IMG_7800.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350758925345488899/IMG_8579.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350760504597282817/IMG_8759.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350760524675547136/IMG_8769.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350759567132590090/IMG_8758.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350759199178752020/IMG_8677.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350759374744059904/IMG_8706.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350761591521673217/IMG_8856.JPG",
                     "https://cdn.discordapp.com/attachments/319845258433396737/350762113267925002/IMG_9159.JPG"]
        await ctx.send(content=":eyes: Luna? :heart:",
                       file=(await self.bytes_download(ctx, choice(chip_list), "jpg")))

    @command()
    async def tea(self, ctx):
        """Tea, Earl Grey, Hot."""
        await ctx.send(content="Earl Grey, Hot.",
                       file=(await self.bytes_download(ctx,
                                                       "https://25.media.tumblr.com/tumblr_lvt63munZQ1qf4elio1_250.gif",
                                                       "gif")))

    @group()
    async def opt(self, ctx):
        """Add or remove an available role."""
        pass

    @opt.command(name="in")
    async def in_(self, ctx, *, role: discord.Role=None):
        """Adds a role. Available Role(s): Roleplayer"""
        roles = [discord.utils.get(ctx.guild.roles, name="Roleplayer")]
        if role:
            if role in roles:
                await ctx.author.add_roles(role, reason=f"Used Opt In Command.")
                msg = await ctx.send(f"Added `{role.name}` from `{ctx.author}`")
                await asyncio.sleep(10)
                await msg.delete()
            else:
                await ctx.send('Invalid Role!')
        else:
            await ctx.send('Please input a role.')

    @opt.command(name="out")
    async def out_(self, ctx, *, role: discord.Role=None):
        """Removes a role. Available Role(s): Roleplayer"""
        roles = [discord.utils.get(ctx.guild.roles, name="Roleplayer")]
        if role in roles:
            await ctx.author.remove_roles(role, reason=f"Used Opt Out Command.")
            msg = await ctx.send(f"Removed `{role.name}` from `{ctx.author}`")
            await asyncio.sleep(10)
            await msg.delete()
        else:
            await ctx.send('Invalid Role!')

    @command(name='weather', aliases=['w', 'conditions'])
    async def get_weather(self, ctx, *, location: str = None):
        """Check the weather in a location"""
        if location is None:
            return await ctx.send('Please provide a location to get Weather Information for.')

        base = f'http://api.apixu.com/v1/current.json?key={self._weather_key}&q={location}'

        try:
            resp, data = await self.bot.fetch(base, return_type='json')
        except asyncio.TimeoutError:
            return await ctx.send('Our Weather API seems to be experiencing difficulties. Please try again later.')

        location = data['location']
        locmsg = f'{location["name"]}, {location["region"]} {location["country"].upper()}'
        current = data['current']

        colour = 0xFFA71A if current['is_day'] != 0 else 0x483078
        embed = discord.Embed(title=f'Weather for {locmsg}',
                              description=f'*{current["condition"]["text"]}*',
                              colour=colour)
        embed.set_thumbnail(url=f'http:{current["condition"]["icon"]}')
        embed.add_field(name='Temperature', value=f'{current["temp_c"]}°C | {current["temp_f"]}°F')
        embed.add_field(name='Feels Like', value=f'{current["feelslike_c"]}°C | {current["feelslike_f"]}°F')
        embed.add_field(name='Precipitation', value=f'{current["precip_mm"]} mm')
        embed.add_field(name='Humidity', value=f'{current["humidity"]}%')
        embed.add_field(name='Windspeed', value=f'{current["wind_kph"]} kph | {current["wind_mph"]} mph')
        embed.add_field(name='Wind Direction', value=current['wind_dir'])
        embed.timestamp = datetime.datetime.utcnow()

        await ctx.send(content=None, embed=embed)

    @command(name='colour', aliases=['color', 'col'])
    async def show_colour(self, ctx, colour: str):
        """Display a colour and popular scheme, from a HEX or RGB."""
        if ctx.message.mentions:
            colour = ctx.message.mentions[0].colour
        else:
            colour = colour.strip('#').strip('0x').replace(' ', ',')

        base = 'http://www.thecolorapi.com/id?format=json&hex={}'
        basep = 'http://www.colourlovers.com/api/palettes?hex={}&format=json'

        if ',' in colour:
            rgb = tuple(map(int, colour.split(',')))
            for x in rgb:
                if x < 0 or x > 255:
                    return await ctx.send('You have entered an invalid colour. Try entering a Hex-Code or R,G,B')
            colour = '%02x%02x%02x' % rgb

        url = base.format(colour)
        urlp = basep.format(colour)

        try:
            resp, data = await self.bot.fetch(url, return_type='json')
        except:
            return await ctx.send('There was a problem with the request. Please try again.')
        else:
            if resp.status > 300:
                return await ctx.send('There was a problem with the request. Please try again.')

        try:
            data['code']
        except KeyError:
            pass
        else:
            return await ctx.send('You have entered an invalid colour. Try entering a Hex-Code or R,G,B')

        try:
            resp, datap = await self.bot.fetch(urlp, return_type='json')
        except:
            pass

        try:
            image = datap[0]['imageUrl']
            colours = datap[0]['colors']
        except:
            image = f'https://dummyimage.com/300/{data["hex"]["clean"]}.png'
            colours = None

        emcol = f"0x{data['hex']['clean']}"
        embed = discord.Embed(title=f'Colour - {data["name"]["value"]}', colour=int(emcol, 0))
        embed.set_thumbnail(url=f'https://dummyimage.com/150/{data["hex"]["clean"]}.png')
        embed.set_image(url=image)
        embed.add_field(name='HEX', value=f'{data["hex"]["value"]}')
        embed.add_field(name='RGB', value=f'{data["rgb"]["value"]}')
        embed.add_field(name='HSL', value=f'{data["hsl"]["value"]}')
        embed.add_field(name='HSV', value=f'{data["hsv"]["value"]}')
        embed.add_field(name='CMYK', value=f'{data["cmyk"]["value"]}')
        embed.add_field(name='XYZ', value=f'{data["XYZ"]["value"]}')
        if colours:
            embed.add_field(name='Scheme:', value=' | '.join(colours), inline=False)

        await ctx.send(content=None, embed=embed)

    @group(invoke_without_command=True)
    async def nasa(self, ctx):
        """Various Commands to access Photos and Information from NASA."""
        pass

    @nasa.command(name='curiosity')
    async def curiosity_photos(self, ctx, camerainp: str = None, date: str = None):
        """Retrieve photos from Mars Rover: Curiosity.
        If date is None, the latest photos will be returned. A date is not guaranteed to have photos.
        If camera is None, a random camera will be chosen. A camera is not guaranteed to have photos.
        Cameras: [FHAZ     : Front Hazard Avoidance Camera]
                 [RHAZ     : Rear Hazard Avoidance Camera]
                 [MAST     : Mast Camera]
                 [CHEMCAM  : Chemistry and Camera Complex]
                 [MAHLI    : Mars Hand Lens Imager]
                 [MARDI    : Mars Descent Imager]
                 [NAVCAM   : Navigation Camera]
                 """

        base = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol={}&camera={}&api_key={}'
        basenc = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol={}&api_key={}'

        cameras = ['fhaz', 'rhaz', 'mast', 'chemcam', 'mahli', 'mardt', 'mardi', 'navcam']

        if camerainp is None:
            camera = 'none'
        else:
            camera = camerainp.lower()

        if camerainp and camerainp.lower() != 'none':

            if camera not in cameras:
                return await ctx.send('You have entered an invalid camera. Valid Cameras:\n'
                                      '```ini\n'
                                      '[FHAZ     : Front Hazard Avoidance Camera]\n'
                                      '[RHAZ     : Rear Hazard Avoidance Camera]\n'
                                      '[MAST     : Mast Camera]\n'
                                      '[CHEMCAM  : Chemistry and Camera Complex]\n'
                                      '[MAHLI    : Mars Hand Lens Imager]\n'
                                      '[MARDI    : Mars Descent Imager]\n'
                                      '[NAVCAM   : Navigation Camera]\n'
                                      '```')

        if date is None or date == 'random':

            url = f'https://api.nasa.gov/mars-photos/api/v1/manifests/Curiosity/?max_sol&api_key={self._nasa_key}'
            try:
                res, sol = await self.bot.fetch(url=url, timeout=15, return_type='json')
            except:
                return await ctx.send('There was an error with your request. Please try again later.')

            if date == 'random':
                if camera and camera != 'none':
                    base = base.format(randint(0, sol["photo_manifest"]["max_sol"]), camera, self._nasa_key)
                else:
                    base = basenc.format(randint(0, sol["photo_manifest"]["max_sol"]), self._nasa_key)
            else:
                if camera and camera != 'none':
                    base = base.format(sol["photo_manifest"]["max_sol"], camera, self._nasa_key)
                else:
                    base = basenc.format(sol["photo_manifest"]["max_sol"], self._nasa_key)
            date = sol["photo_manifest"]["max_sol"]
        else:
            if camera and camera != 'none':
                base = f'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?' \
                       f'earth_date={date}' \
                       f'&camera={camera}' \
                       f'&api_key={self._nasa_key}'
            else:
                base = f'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?' \
                       f'earth_date={date}' \
                       f'&api_key={self._nasa_key}'

        try:
            res, data = await self.bot.fetch(base, timeout=15, return_type='json')
        except:
            return await ctx.send('There was an error with your request. Please try again later.')

        if len(data['photos']) <= 0:
            return await ctx.send(f'There was no photos available on date/sol'
                                  f' `{date}` with camera `{camera.upper() if camera else "NONE"}`.')

        photos = data['photos']
        main_img = choice(photos)

        if len(photos) > 4:
            photos = sample(photos, 4)

        embed = discord.Embed(title='NASA Rover: Curiosity', description=f'Date/SOL: {date}', colour=0xB22E20)
        embed.set_image(url=main_img['img_src'])
        embed.add_field(name='Camera', value=camera.upper())
        embed.add_field(name='See Also:',
                        value='\n'.join(x['img_src'] for x in photos[:3]) if len(photos) > 3 else 'None',
                        inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text='Generated on ')
        await ctx.send(content=None, embed=embed)

    @nasa.command(name='apod', aliases=['iotd'])
    async def nasa_apod(self, ctx):
        """Returns NASA's Astronomy Picture of the day."""
        # todo Add the ability to select a date.

        url = f'https://api.nasa.gov/planetary/apod?api_key={self._nasa_key}'
        try:
            res, data = await self.bot.fetch(url=url, timeout=15, return_type='json')
        except:
            return await ctx.send('There was an error processing your request')

        embed = discord.Embed(title='Astronomy Picture of the Day',
                              description=f'**{data["title"]}** | {data["date"]}',
                              colour=0x1d2951)
        embed.add_field(name='Explanation',
                        value=data['explanation'] if len(data['explanation']) < 1024
                        else f"{data['explanation'][:1020]}...", inline=False)
        embed.add_field(name='HD Download', value=f'[Click here!]({data["hdurl"]})')
        embed.set_image(url=data['url'])
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text='Generated on ')

        await ctx.send(content=None, embed=embed)

    @nasa.command(name='epic', aliases=['EPIC'])
    async def nasa_epic(self, ctx):
        """Returns NASA's most recent EPIC image."""

        base = f'https://api.nasa.gov/EPIC/api/natural?api_key={self._nasa_key}'
        img_base = 'https://epic.gsfc.nasa.gov/archive/natural/{}/png/{}.png'

        try:
            res, data = await self.bot.fetch(base, timeout=15, return_type='json')
        except:
            return await ctx.send('There was an error processing your request. Please try again.')

        img = choice(data)
        coords = img['centroid_coordinates']

        embed = discord.Embed(title='NASA EPIC', description=f'*{img["caption"]}*', colour=0x1d2951)
        embed.set_image(url=img_base.format(img['date'].split(' ')[0].replace('-', '/'), img['image']))
        embed.add_field(name='Centroid Coordinates',
                        value=f'Lat: {coords["lat"]} | Lon: {coords["lon"]}')
        embed.add_field(name='Download',
                        value=img_base.format(img['date'].split(' ')[0].replace('-', '/'), img['image']))
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text='Generated on ')

        await ctx.send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
