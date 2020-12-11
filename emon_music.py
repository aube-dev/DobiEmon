import discord

import emon_magics as dem


music_queue = []


class Track:
    __slots__ = 'path', 'status'

    def __init__(self, path, status='NOT PLAYING'):
        self.path = path
        self.status = status

    def get_title(self):
        return str(self.path).replace('musics\\', '')

    def play(self):
        self.status = 'PLAYING'

    def stop(self):
        self.status = 'NOT PLAYING'


def create_audio_source(path):
    audio_source = discord.FFmpegPCMAudio(str(path), executable='C:\\ffmpeg\\bin\\ffmpeg.exe', options='-vn -b:a 128k -vol 50')
    audio_source = discord.PCMVolumeTransformer(audio_source)
    return audio_source


def add_queue(track):
    music_queue.append(track)


def clean_queue():
    global music_queue
    for track in music_queue:
        track.stop()
    music_queue = []


async def play_music(ctx, bot):
    guild: discord.Guild = ctx.guild
    vc: discord.VoiceClient = guild.voice_client

    def after_play(error):
        if not error and not vc.is_playing():
            if not music_queue:
                return
            last_track = music_queue[0]
            last_track.stop()
            del music_queue[0]

            if vc and music_queue:
                next_track = music_queue[0]
                next_track_audio_source = create_audio_source(next_track.path)
                vc.play(next_track_audio_source, after=after_play)
                next_track.play()
                dem.run_coroutine(dem.send_embed(ctx, '음악 재생이 시작됩니다.', '음악 제목 : ' + next_track.get_title()), bot)
            elif vc and not music_queue:
                dem.run_coroutine(vc.disconnect(), bot)

    if vc.is_playing():
        return

    if vc and music_queue:
        track = music_queue[0]
        audio_source = create_audio_source(track.path)
        vc.play(audio_source, after=after_play)
        track.play()
        await dem.send_embed(ctx, '음악 재생이 시작됩니다.', '음악 제목 : ' + track.get_title())
