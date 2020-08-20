import asyncio, time, urllib.request, json, csv, random 
from twitchio.ext import commands
from kasa import SmartStrip

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(irc_token='#', client_id='#', nick='lemonman96', prefix='!', initial_channels=['#lemonman96'])
        self.voter_list = []

        #in seconds
        self.vote_delay = 90 #set to 90 when deployed
        self.kill_delay = 600 #set to 600 when deployed
        
        self.cooldown_end = 0
        self.is_cooldown = False
        self.ycount = 0
        self.ncount = 0
        self.start_vote = False

    async def event_ready(self):
        ws = self._ws
        print('Killbot successfully started!')
        await ws.send_privmsg(content='Killbot joined!', channel=self.nick)

    async def event_join(self, user):
        ws = self._ws
        await ws.send_privmsg(content='Welcome ' + user.name + '! Please use !kill to initiate kill vote, see rules for more information', channel=self.nick)

    async def event_command_error(self, ctx, error):
        if type(error) == commands.errors.CommandNotFound:
            await ctx.send(ctx.author.name + ', that command doesn\'t exist. Please use !kill to initiate a vote!')
    
    async def isMod(self, ctx):
        return ctx.author.is_mod

    async def isOnCooldown(self, ctx):
        if(self.is_cooldown):
            time_remaining = int(self.cooldown_end - time.time())
            await ctx.send(f'Kill is on cooldown. Please wait {time_remaining} seconds.')
            #await ctx.send(f'Kill is on cooldown.')
        return self.is_cooldown

    async def kill_wait(self):
        self.is_cooldown = True
        await asyncio.sleep(self.kill_delay)
        self.is_cooldown = False

    #method to send message when voters try to vote w/out starting vote
    async def voteCheck(self, ctx):
        if(not self.start_vote):
            await ctx.send(f'Vote not started, please use !kill first.')
        return self.start_vote

    #sends message for multiple vote calls
    async def voteInEffect(self, ctx):
        if(self.start_vote):
            await ctx.send(f'Vote already started!')
        return self.start_vote

    @commands.command(name='kill')
    async def kill(self, ctx):
        if not await self.isOnCooldown(ctx) and not await self.voteInEffect(ctx):
            print('vote started...')
            self.start_vote = True
            dev = SmartStrip("192.168.0.165")
            await dev.update()
            await ctx.send(f'Kill vote started, type !y or !n in chat!')
            #vote delay
            await asyncio.sleep(self.vote_delay)
            print('vote ended...')
            #handle pass/fail and reset vote bool
            if(self.ycount > self.ncount):
                await ctx.send(f'Vote passed!')
                print(self.cooldown_end)
                self.cooldown_end = time.time() + self.kill_delay
                
                #reboot plug1
                await dev.children[0].turn_off()
                await asyncio.sleep(1)
                await dev.children[0].turn_on()

                print('on cooldown...')
                await self.kill_wait()
                print('off cooldown...')
                
            else:
                await ctx.send(f'Vote failed!')
            self.ycount = 0
            self.ncount = 0
            self.voter_list = []
            self.start_vote = False
            print('reset!')
    
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
    
    

