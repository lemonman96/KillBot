import asyncio, time, urllib.request, json, csv, random 
from twitchio.ext import commands
from kasa import SmartStrip

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(irc_token='#', client_id='#', nick='lemonman96', prefix='!', initial_channels=['#lemonman96'])
        self.voter_list = []
        #in seconds
        self.vote_delay = 10
        self.ycount = 0
        self.ncount = 0
        self.start_vote = False

    async def event_ready(self):
        ws = bot._ws
        print('Killbot successfully started!')
        await ws.send_privmsg(content='Killbot joined!', channel=self.nick)

    async def event_join(self, user):
        ws = bot._ws
        await ws.send_privmsg(content='Welcome ' + user.name + '! Please use !kill to initiate kill vote, see rules for more information', channel=self.nick)

    async def event_command_error(self, ctx, error):
        if type(error) == commands.errors.CommandNotFound:
            await ctx.send(ctx.author.name + ', that command doesn\'t exist. Please use !kill to initiate a vote!')
    
    async def isMod(ctx):
        return ctx.author.is_mod

    async def voteCheck(self, ctx):
        if(self.start_vote):
            return True
        await ctx.send(f'Vote not started, please use !kill first.')
        return False

    @commands.command(name='kill')
    async def kill(self, ctx):

        self.start_vote = True
        dev = SmartStrip("192.168.0.165")
        await ctx.send(f'Kill vote started, type !y or !n in chat!')
        #vote delay
        await asyncio.sleep(self.vote_delay)

        #handle pass/fail and reset vote bool
        if(self.ycount > self.ncount):
            await ctx.send(f'Vote passed!')
            await dev.reboot()
            #await dev.turn_off()
        else:
            await ctx.send(f'Vote failed!')
        self.ycount = 0
        self.ncount = 0
        self.voter_list = []
        self.start_vote = False
    
    @commands.check(isMod)
    @commands.command(name='spin')
    async def spin(self, ctx):
        with open('collection.csv', 'r', encoding="utf-8") as file:
            reader = csv.reader(file)
            reader = list(reader)
            num = random.randrange(1, len(reader) - 1)
            await ctx.send(reader[num][1] + ' for ' + reader[num][2] + ' has been picked!')


    @commands.command(name='y')
    async def y(self, ctx):
        if await self.voteCheck(ctx):
            if ctx.author in self.voter_list:
                await ctx.send(ctx.author.name + ' already voted!')
            else:
                self.ycount += 1
                self.voter_list.append(ctx.author)
        
    @commands.command(name='n')
    async def n(self, ctx):
        if await self.voteCheck(ctx):
            if ctx.author in self.voter_list:
                await ctx.send(ctx.author.name + ' already voted!')
            else:
                self.ncount += 1
                self.voter_list.append(ctx.author)     
    
    

bot = Bot()
bot.run()