import discord
from discord.ext import commands
import math
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import cmath
import collections
import time
import asyncio
import functools
import io
import random
import secrets
import re

okay = [[1, 1, 1],
        [1, 1, 2],
        [1, 2, 2],
        [1, 1, 3],
        [1, 2, 3],
        [18, 23, 27]]

_OFFSET = 2 ** 3217 - 1

_seed = 0


def _scale(old_min, old_max, new_min, new_max, value):
    return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min


def _lerp(v0, v1, t):
    return v0 + t * (v1 - v0)


def _lerp_color(c1, c2, t):
    return tuple(round(_lerp(v1, v2, t)) for v1, v2 in zip(c1, c2))


_lerp_pink = functools.partial(_lerp_color, (0, 0, 0), (255, 105, 180))


async def _change_ship_seed():
    global _seed
    while True:
        _seed = secrets.randbits(256)
        next_delay = random.uniform(10, 60) * 60
        await asyncio.sleep(next_delay)


def _user_score(user):
    return (user.id
            + int(user.avatar or str(user.default_avatar.value), 16)
            + sum(ord(c) * 0x10FFFF * i for i, c in enumerate(user.name))
            + int(user.discriminator)
            )


_default_rating_comments = (
    'There is no chance for this to happen.',
    'Why...',
    'No way, not happening.',
    'Nope.',
    'Maybe.',
    'Woah this actually might happen.',
    'owo what\'s this',
    'You\'ve got a chance!',
    'Definitely.',
    'What are you waiting for?!',
)


_value_to_index = functools.partial(_scale, 0, 100, 0, len(_default_rating_comments) - 1)


class _ShipScore(collections.namedtuple('_ShipRating', 'score comment')):
    __slots__ = ()

    def __new__(cls, score, comment=None):
        if comment is None:
            index = round(_value_to_index(score))
            print(index)
            comment = _default_rating_comments[index]
        return super().__new__(cls, score, comment)


# List of possible ratings when someone attempts to ship themselves
_self_ratings = [
    "Rip {user}, they're forever alone...",
    "Selfcest is bestest.",
]


def _calculate_rating(user1, user2):
    if user1 == user2:
        index = _seed % 2
        return _ShipScore(index * 100, _self_ratings[index].format(user=user1))

    score = ((_user_score(user1) + _user_score(user2)) * _OFFSET + _seed) % 100
    return _ShipScore(score, comment=None)


class Circle:
    def __init__(self, x, y, r):
        """
            I probably don't need self.x or self.y with self.m...
            but I don't feel comfortable working with complex numbers yet :(
        """
        self.r = r
        self.x = x
        self.y = y
        self.m = (x + y * 1j)

    def __hash__(self):
        return self.r + self.x + self.y

    def __eq__(self, c):
        if isinstance(c, Circle):
            return self.r == c.r and self.x == c.x and self.y == c.y

    def curv(self):
        """
            Curvature of a circle is apparently the inverse of its radius...
            Who knew?
        """
        return 1 / self.r

    @property
    def bound(self):
        """
            Returns the upper left and bottom right coordinates that bound the circle
        """
        r = abs(self.r.real)
        return (int(self.x - r), int(self.y - r), int(self.x + r), int(self.y + r))

    @property
    def size(self):
        """
            For some reason self.r turns into an imaginary number...
            I don't know why?
        """
        return abs(self.r.real)

    def correct(self, cx, cy):
        """
            Literally just shifts the center of the circle off by whatever cx and cy are
        """
        self.x += cx
        self.y += cy
        self.m = (self.x + self.y * 1j)

    def resize(self, factor):
        """
            With any luck, this rezies the circle with respect to the origin?
            Should maintain kissing
        """
        self.x *= factor
        self.y *= factor
        self.r *= factor
        self.m = (self.x + self.y * 1j)


class MyCircles:
    def __init__(self, r1, r2, r3):
        self.circles = list(self.tang(1 / r1, 1 / r2, 1 / r3))
        self.big = self.circles[0]
        self.todo = collections.deque()

    @property
    def num(self):
        return len(self.circles)

    def outer(self, c1, c2, c3):
        """Quality function that takes 3 circles and finds the outer circle what kisses all three"""
        cur1 = c1.curv()
        cur2 = c2.curv()
        cur3 = c3.curv()
        m1 = c1.m
        m2 = c2.m
        m3 = c3.m
        cur4 = cur1 + cur2 + cur3 - 2 * cmath.sqrt(cur1 * cur2 + cur2 * cur3 + cur3 * cur1)  # Descartes theorem
        m4 = (cur1 * m1 + cur2 * m2 + cur3 * m3 - 2 * cmath.sqrt(
            cur1 * m1 * cur2 * m2 + cur2 * m2 * cur3 * m3 + cur3 * m3 * cur1 * m1)) / cur4  # Magic
        return Circle(m4.real, m4.imag, 1 / cur4)

    def tang(self, r2, r3, r4):
        """Quality function that takes 3 radiuses and makes 4 circles that are kissing"""
        c2 = Circle(0, 0, r2)  # The first circle is placed at the origin
        c3 = Circle(r2 + r3, 0, r3)  # The second circle is placed kissing the first circle to the right
        x = (r2 * r2 + r2 * r4 + r2 * r3 - r3 * r4) / (
        r2 + r3)  # Magic triangle maths to figure out where the of the third circle should go
        y = cmath.sqrt((r2 + r4) * (r2 + r4) - x * x)
        c4 = Circle(x.real, y.real, r4)
        c1 = self.outer(c2, c3, c4)  # The outer circle is generated based on the first 3
        offx = 0 - c1.x
        offy = 0 - c1.y
        c2.correct(offx, offy)  # Offsets all the circles so the biggest circle is centered instead of the first circle
        c3.correct(offx, offy)
        c4.correct(offx, offy)
        c1.correct(offx, offy)
        return c1, c2, c3, c4

    def sec(self, fixed, c1, c2, c3):
        """
            Quality function that takes one fixed circle and three circles.
            A new circle is generated such that it kisses the three circles but not the fixes circle.
        """
        curf = fixed.curv()
        cur1 = c1.curv()
        cur2 = c2.curv()
        cur3 = c3.curv()
        curn = 2 * (cur1 + cur2 + cur3) - curf
        mn = (2 * (cur1 * c1.m + cur2 * c2.m + cur3 * c3.m) - curf * fixed.m) / curn
        return Circle(mn.real, mn.imag, 1 / curn)

    def fakerecursion(self, depth):
        """
            Fucking python won't let me do recursion properly so its 100% faked with a dequeue and a while loop
        """
        curdepth = 0
        self.todo.append(self.circles + [curdepth])
        while curdepth < depth:
            c1, c2, c3, c4, curdepth = self.todo.popleft()
            if curdepth == 0:
                cn1 = self.sec(c1, c2, c3, c4)
                self.circles.append(cn1)
                self.todo.append([cn1, c2, c3, c4, curdepth + 1])
            cn2 = self.sec(c2, c1, c3, c4)
            if cn2 not in self.circles:
                self.circles.append(cn2)
            else:
                print("dup")
            self.todo.append([cn2, c1, c3, c4, curdepth + 1])
            cn3 = self.sec(c3, c1, c2, c4)
            if cn3 not in self.circles:
                self.circles.append(cn3)
            else:
                print("dup")
            self.todo.append([cn3, c1, c2, c4, curdepth + 1])
            cn4 = self.sec(c4, c1, c2, c3)
            if cn4 not in self.circles:
                self.circles.append(cn4)
            else:
                print("dup")
            self.todo.append([cn4, c1, c2, c3, curdepth + 1])


class Images:
    def __init__(self, bot):
        self.bot = bot
        self.wew = {'C': 'You too~!',
                        'M': 'I will not!'}
        self._mask = open('./resources/heart.png', 'rb')
        self._future = asyncio.ensure_future(_change_ship_seed())

    @commands.command(hidden=True)
    async def ute(self, ctx):
        pre = self.bot.command_prefix(self.bot, ctx.message)
        msg = self.wew.get(pre, 'I don\'t know what to say to that...')
        await ctx.send(msg)

    @commands.command(hidden=True)
    async def setute(self, ctx, *, text: str = None):
        if text is None:
            await ctx.send('I don\'t know what to say to that...')
        else:
            pre = self.bot.command_prefix(self.bot, ctx.message)
            self.wew[pre] = text
            await ctx.send('\U0001f44c')

    @commands.command()
    async def quilt(self, ctx, *people: discord.Member):
        """Draws a canvas of avatars."""
        if len(people) == 0:
            people = [ctx.author]
        avatars = []
        for person in people:
            async with ctx.session.get(person.avatar_url_as(format='png', size=512)) as r:
                avatars.append(BytesIO(await r.read()))
        file = await self.bot.loop.run_in_executor(None, self._quilt, avatars)
        await ctx.send(file=file)

    def _quilt(self, avatars):
        """
            Makes a quilt of avatars of avatars that tries to be as square as possible
        """
        xbound = math.ceil(math.sqrt(len(avatars)))
        ybound = math.ceil(len(avatars) / xbound)
        size = int(2520 / xbound)
        base = Image.new(mode='RGBA', size=(xbound * size, ybound * size), color=(0, 0, 0, 0))
        x, y = 0, 0
        for avatar in avatars:
            im = Image.open(avatar)
            base.paste(im.resize((size, size), resample=Image.BILINEAR), box=(x * size, y * size))
            if x < xbound - 1:
                x += 1
            else:
                x = 0
                y += 1
        buffer = BytesIO()
        base.save(buffer, 'png')
        buffer.seek(0)
        return discord.File(buffer, filename='quilt.png')

    @commands.command()
    async def avatars(self, ctx, *people: discord.Member):
        """
            Makes a Apollonian gasket of avatars of people of your choice
        """
        if len(people) == 0:
            people = [ctx.author]
        datas = []
        async with ctx.channel.typing():
            for p in people:
                async with ctx.session.get(p.avatar_url_as(format='png')) as r:
                    datas.append(BytesIO(await r.read()))
            stime = time.monotonic()
            starting = random.choice(okay)
            random.shuffle(starting)
            file, i = await self.bot.loop.run_in_executor(None, self._fucker, 5, datas, False, starting)
            await ctx.send(f'*{i} Avatars drawn in {(time.monotonic() - stime)*1000:.2f}ms*', file=file)

    @commands.command()
    async def circles(self, ctx):
        """
            Makes a Apollonian gasket of uploaded attachments.
            Will fuck them up with resizing non-square images because I haven't decided how to crop them yet
        """
        if len(ctx.message.attachments) == 0:
            return
        datas = []
        async with ctx.channel.typing():
            for p in ctx.message.attachments:
                if p.width:
                    async with ctx.session.get(p.url) as r:
                        datas.append(BytesIO(await r.read()))
            if len(datas) == 0:
                return
            stime = time.monotonic()  # Someone go fix this
            startingstuff = random.choice(okay)
            print(startingstuff)
            random.shuffle(startingstuff)
            print(startingstuff)
            file, i = await self.bot.loop.run_in_executor(None, self._fucker, 5, datas, False, startingstuff)
            await ctx.send(f'*{i} Avatars drawn in {(time.monotonic() - stime)*1000:.2f}ms*', file=file)

    @commands.command()
    async def avyserver(self, ctx):
        """Makes an Apollonian Gasket of all the members of the server."""
        members = ctx.guild.members
        msg = await ctx.send("Hold on this is gonna take some time...")
        await ctx.invoke(self.bot.get_command('avatars'),
                         *random.sample(members, len(members) if len(members) <= 50 else 50))
        await asyncio.sleep(10)
        await msg.delete()

    def _fucker(self, depth, data, firstlayer, starting):
        imgsize = 400
        asdf = MyCircles(starting[0], starting[1], starting[2])
        factor = ((
                  imgsize / 2) - 1) / asdf.big.size
        # After initializing the first 4 circles from the 3 radiuses(?), resize them such that they fill imgsize
        for c in asdf.circles:
            c.resize(factor)
        asdf.fakerecursion(depth)  # This is where the magic happens
        im = Image.new('RGBA', (imgsize, imgsize), color=(0, 0, 0, 0))
        maska = Image.new('RGBA', (1024, 1024), color=(0, 0, 0, 0))
        maskb = Image.new('L', (1024, 1024), color=255)
        draw = ImageDraw.Draw(maskb)
        draw.ellipse(((0, 0), (1024, 1024)), fill=0)
        del draw
        maska.putalpha(maskb)
        imgs = collections.deque()
        for d in data:
            temp = Image.open(d).resize((1024, 1024), resample=Image.BILINEAR).convert('RGBA')
            avymask = temp.split()[3]
            avymask.paste(maska, (0, 0, 1024, 1024), maska)
            temp.putalpha(
                avymask)
            imgs.append(temp)
        i = 0
        first = True
        for a in asdf.circles:
            if not firstlayer and first:
                first = False
                continue
            a.correct(imgsize / 2, imgsize / 2)
            x, y = a.bound[2] - a.bound[0], a.bound[3] - a.bound[1]
            if not x or not y:
                continue
            curr = imgs.popleft()
            temp = curr.resize((x, y), resample=Image.BILINEAR)
            im.paste(temp, box=a.bound, mask=temp)
            imgs.append(curr)
            i += 1
        bb = BytesIO()
        im.save(bb, 'png')
        bb.seek(0)
        return discord.File(bb, filename='fuckery.png'), i

    def __unload(self):
        self._mask.close()
        self._future.cancel()

    async def _load_user_avatar(self, user):
        url = user.avatar_url_as(format='png', size=512)
        async with self.bot.session.get(url) as r:
            return await r.read()

    def _create_ship_image(self, score, avatar1, avatar2):
        ava_im1 = Image.open(avatar1).convert('RGBA')
        ava_im2 = Image.open(avatar2).convert('RGBA')

        size = min(ava_im1.size, ava_im2.size)
        offset = round(_scale(0, 100, size[0], 0, score))

        ava_im1.thumbnail(size)
        ava_im2.thumbnail(size)

        newimg1 = Image.new('RGBA', size=size, color=(0, 0, 0, 0))
        newimg1.paste(ava_im2, (-offset, 0))
        newimg1.paste(ava_im1, (offset, 0))

        newimg2 = Image.new('RGBA', size=size, color=(0, 0, 0, 0))
        newimg2.paste(ava_im1, (offset, 0))
        newimg2.paste(ava_im2, (-offset, 0))

        im = Image.blend(newimg1, newimg2, alpha=0.6)

        mask = Image.open(self._mask).convert('L')
        mask = mask.resize(ava_im1.size, resample=Image.BILINEAR)
        im.putalpha(mask)

        f = io.BytesIO()
        im.save(f, 'png')
        f.seek(0)
        return discord.File(f, filename='test.png')

    async def _ship_image(self, score, user1, user2):
        user_avatar_data1 = io.BytesIO(await self._load_user_avatar(user1))
        user_avatar_data2 = io.BytesIO(await self._load_user_avatar(user2))
        return await self.bot.loop.run_in_executor(None, self._create_ship_image, score,
                                                   user_avatar_data1, user_avatar_data2)

    @commands.command()
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member=None):
        """Ships two users together, and scores accordingly."""
        if user2 is None:
            user1, user2 = ctx.author, user1

        score, comment = _calculate_rating(user1, user2)
        file = await self._ship_image(score, user1, user2)
        colour = discord.Colour.from_rgb(*_lerp_pink(score / 100))

        embed = (discord.Embed(colour=colour, description=f"{user1.mention} x {user2.mention}")
                 .set_author(name='Shipping')
                 .add_field(name='Score', value=f'{score}/100')
                 .add_field(name='\u200b', value=f'*{comment}*', inline=False)
                 .set_image(url='attachment://test.png')
                 )
        await ctx.send(file=file, embed=embed)

    @commands.command(usage='<line 1> [line 2] [line 3]')
    async def retro(self, ctx, line_1: str, line_2: str = '', *, line_3: str = ''):
        """Credits: ReinaSakuraba (Reina#0277)"""
        if not re.fullmatch(r'[A-Za-z0-9 ]+', line_1):
            return await ctx.send('First line only supports alphanumerical characters.')

        data = {
            'bcg': random.randint(1, 5),
            'txt': random.randint(1, 4),
            'text1': line_1,
            'text2': line_2,
            'text3': line_3,
        }

        async with ctx.session.post('https://photofunia.com/effects/retro-wave', data=data) as r:
            txt = await r.text()

        link = re.search(r'(https?.+?.jpg\?download)', txt)
        async with ctx.session.get(link.group(1)) as r:
            await ctx.send(file=discord.File(io.BytesIO(await r.read()), 'retro.jpg'))

    @commands.command(aliases=["twilightzone"])
    async def tzone(self, ctx, content: str):
        """You unlock this door with the key of imagination

        Credits: Letharrick#9181
        """
        x = functools.partial(self._tzone, content)
        tzone_image = await self.bot.loop.run_in_executor(None, x)

        await ctx.send(file=discord.File(tzone_image, filename="{}.png".format(content)))

    def _tzone(self, content: str):
        content = content.upper()
        img = Image.open("./resources/twilightzone.png")
        img_w, img_h = (1280, 900)

        font = ImageFont.truetype("./resources/twilightzone.ttf", 200)
        draw = ImageDraw.Draw(img)
        t_w, t_h = draw.textsize(content, font)
        draw.text(((img_w - t_w) / 2, (img_h - t_h) / 2), content, (192, 192, 192), font=font)

        bytesio = BytesIO()
        img.save(bytesio, "png")
        bytesio.seek(0)

        return bytesio


def setup(bot):
    bot.add_cog(Images(bot))
