import asyncio
import discord
import time
from discord.ext import commands
if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')


def __init__(self, bot):
        self.bot = bot

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = ' {0.title} 업로더: {0.uploader} 신청자: {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [길이: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() 
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, '이제' + str(self.current)+'가 재생됨')
            self.current.player.start()
            await self.play_next_song.wait()
class Music:
    
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx, *, channel : discord.Channel):
        """보이스 채널에 참가하게 함."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('이미 보이스 채널안이야')
        except discord.InvalidArgument:
            await self.bot.say('이건 보이스 채널이 아님.')
        else:
            await self.bot.say('노래부를 준비 완료 **' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def 들어와(self, ctx):
        """재혁봇을 보이스채널에 들어오게 함 ."""
        summoned_channel = ctx.message.author.voice_channel
        await self.bot.say('님들 ㅎㅇ')
        if summoned_channel is None:
            await self.bot.say('채널에 너 있는거 확실함?')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)
        return True

        
    
    @commands.command(pass_context=True, no_pm=True)
    async def 틀어(self, ctx, *, song : str):
        """유튜브 링크의 음악을 재생 ( 틀어 [유튜브링크] )"""
        
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            await self.bot.say("좀 기다려")
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'ㅋ  : ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('부를노래 : ' + str(entry))
            await state.songs.put(entry)
  
    @commands.command(pass_context=True, no_pm=True)
    async def 갓곡틀어(self, ctx):
        """갓곡을 재생함"""
        song = 'https://www.youtube.com/watch?v=9rLMvRwpGX8'
        
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
               return
        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'ㅋ  : ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            await self.bot.say('갓 ㅡㅡㅡㅡㅡㅡㅡㅡㅡ곡')
            entry = VoiceEntry(ctx.message, player)
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def 볼륨(self, ctx, value : int):
        """재생중인 노래의 볼륨 조정"""
        state = self.get_voice_state(ctx.message.server)
        if value < 10:
            await self.bot.say('볼륨은 10이상으로 듣자')
        elif value >=500:
            await self.bot.say('용준이인줄;')
            return False
        elif state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('볼륨을 {:.0%}로 조정'.format(player.volume))
            
    @commands.command(pass_context=True, no_pm=True)
    async def 멈춰(self, ctx):
       
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

        
    @commands.command(pass_context=True, no_pm=True)
    async def 꺼져(self, ctx):
        """재혁이를 보이스채널에서 꺼지게함"""
        state = self.get_voice_state(ctx.message.server)
        voter = ctx.message.author
        if voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                 server = ctx.message.server
                 state = self.get_voice_state(server)
                 if state.is_playing():
                    player = state.player
                    player.stop()

                 try: 
                    state.audio_player.cancel()
                    del self.voice_states[server.id]
                    await state.voice.disconnect()
                    await self.bot.say("3명이나 원한다면 나가드림 ㅃ")
                 except:
                    pass
            else:
                await self.bot.say('[{}/3]명이 만족해야 나갈꺼임 응 ㅅㄱ'.format(total_votes))
        else:
            await self.bot.say('넌이미 했잖아 너말고')
        server = ctx.message.server
        state = self.get_voice_state(server)
        
       
    
    @commands.command(pass_context=True, no_pm=True)
    async def 넘겨(self, ctx):
        """노래를 넘길지 투표함. 노래신청자가 명령시 바로 넘김
        """
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('노래 안틀고있는데  ㅋㅋ')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('ㅇㅋ노래넘김...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 999:
                await self.bot.say('그렇게 원하면 ㅋㅋ')
                state.skip()
            else:
                await self.bot.say('ㅇㅋ  [{}/2]명 만족하면 넘김  '.format(total_votes))
        else:
            await self.bot.say('이미 투표함 ')

        state = self.get_voice_state(ctx.message.server)
        




    @commands.command(pass_context=True, no_pm=True)
    async def 느금마(self, ctx):
        """장타"""
        await self.bot.say('장타')
        return True

    @commands.command(pass_context=True, no_pm=True)
    async def ㄴㄱㅁ(self, ctx):
        """ㅈㅌ"""
        await self.bot.say('ㅈㅌ')
        return True

             
                           
        
                        

  
            
def setup(bot):
    bot.add_cog(Music(bot))
    print('음악 로딩 완료')
