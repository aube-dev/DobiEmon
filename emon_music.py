import discord

import emon_magics as dem


music_queue = []


class Track:
    __slots__ = 'path', 'message'

    def __init__(self, path, message=None):
        self.path = path
        self.message = message

    def get_title(self):
        return str(self.path).replace('musics\\', '')

    def set_message(self, message):
        self.message = message


def create_audio_source(path):
    audio_source = discord.FFmpegPCMAudio(str(path), executable='C:\\ffmpeg\\bin\\ffmpeg.exe', options='-vn -b:a 128k -vol 50')
    audio_source = discord.PCMVolumeTransformer(audio_source)
    return audio_source


def add_queue(track):
    music_queue.append(track)


def clean_queue():
    global music_queue
    music_queue = []


def get_queue():
    global music_queue
    return music_queue


def skip_music(ctx, bot):
    guild: discord.Guild = ctx.guild
    vc: discord.VoiceClient = guild.voice_client
    if vc:
        vc.stop()
    else:
        dem.run_coroutine(dem.send_embed(ctx, '오류가 발생했습니다.', '음성 채널에 들어가 있지 않습니다.'), bot)


async def play_music(ctx, bot):
    guild: discord.Guild = ctx.guild
    vc: discord.VoiceClient = guild.voice_client

    def after_play(error):
        if not error and not vc.is_playing():
            if not music_queue:
                return
            dem.run_coroutine(music_queue[0].message.delete(), bot)
            del music_queue[0]

            if vc and music_queue:
                next_track = music_queue[0]
                next_track_audio_source = create_audio_source(next_track.path)
                vc.play(next_track_audio_source, after=after_play)
                after_message = dem.run_coroutine(dem.send_embed(ctx, '음악 재생이 시작됩니다.',
                                                                 '음악 제목 : ' + next_track.get_title()), bot)
                next_track.set_message(after_message)
            elif vc and not music_queue:
                dem.run_coroutine(dem.send_embed(ctx, '음악 재생이 완료되었습니다.',
                                                 '재생 대기 목록의 모든 음악이 재생되었습니다. 도비에몽이 퇴장합니다.'), bot)
                dem.run_coroutine(vc.disconnect(), bot)

    if vc.is_playing():
        return

    if vc and music_queue:
        track = music_queue[0]
        audio_source = create_audio_source(track.path)
        vc.play(audio_source, after=after_play)
        message = await dem.send_embed(ctx, '음악 재생이 시작됩니다.', '음악 제목 : ' + track.get_title())
        track.set_message(message)
