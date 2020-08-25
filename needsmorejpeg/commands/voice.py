#!/usr/bin/env python3
from typing import Optional
import subprocess
import discord # import FFmpegAudio
import urllib
import io
import tempfile
import asyncio

from ..bot import bot, commands, is_owner

@bot.command()
async def say(ctx, *args: str):
	"Joins the voice channel you are in and says what you passed to it"
	try:
		voice_channel = ctx.author.voice.channel
		voice_channel.name # raise AttributeError if voice_channel is None
	except AttributeError:
		await ctx.send("Could not find a voice channel")
		raise ValueError

	try:
		espeak = subprocess.Popen(["espeak", "--stdout"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	except FileNotFoundError:
		await ctx.send("Could not open espeak to generate voice")
		raise ValueError

	espeak.stdin.write(' '.join(arg for arg in args).encode())
	espeak.stdin.close()

	# voice_data_wave = espeak.stdout.read()
	voice_data = discord.FFmpegOpusAudio(espeak.stdout, pipe=True)

	if ctx.message.guild.voice_client is not None and ctx.message.guild.voice_client.is_connected():
		voice_client = ctx.message.guild.voice_client
	else:
		voice_client = await voice_channel.connect()

	voice_client.play(voice_data)
	await ctx.message.add_reaction("✅")

@bot.command()
async def leave(ctx):
	"Leaves the voice channel you are in"
	try:
		voice_channel = ctx.author.voice.channel
		voice_channel.name # raise AttributeError if voice_channel is None
	except AttributeError:
		await ctx.send("Could not find a voice channel")
		raise ValueError

	if ctx.message.guild.voice_client is not None and ctx.message.guild.voice_client.is_connected():
		voice_client = ctx.message.guild.voice_client
	else:
		await ctx.send("Could not find a voice channel")
		raise ValueError

	await voice_client.disconnect()
	await ctx.message.add_reaction("✅")

headers = {
	"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv76.0) Gecko/20100101 Firefox 76.0",
}

@bot.command()
#@commands.check(is_owner)
async def play(ctx, arg: Optional[str]):
	"Joins the voice channel you are in and plays what you passed to it"
	try:
		voice_channel = ctx.author.voice.channel
		voice_channel.name # raise AttributeError if voice_channel is None
	except AttributeError:
		await ctx.send("Could not find a voice channel")
		raise ValueError

	if ctx.message.attachments:
		data = await ctx.message.attachments[0].read()
	else:
		request = urllib.request.Request(arg, None, headers=headers)
		response = urllib.request.urlopen(request)
		if not response:
			raise ValueError
		data = response.read()

	file = tempfile.TemporaryFile()
	file.write(data)
	file.seek(0)

	# voice_data_wave = espeak.stdout.read()
	voice_data = discord.FFmpegOpusAudio(file, pipe=True)

	if ctx.message.guild.voice_client is not None and ctx.message.guild.voice_client.is_connected():
		voice_client = ctx.message.guild.voice_client
	else:
		voice_client = await voice_channel.connect()

	voice_client.play(voice_data)
	await ctx.message.add_reaction("✅")

@bot.command()
async def yt(ctx, arg: str):
	"Joins the voice channel you are in and plays what you passed to it"
	try:
		voice_channel = ctx.author.voice.channel
		voice_channel.name # raise AttributeError if voice_channel is None
	except AttributeError:
		await ctx.send("Could not find a voice channel")
		raise ValueError

	fd, filename = tempfile.mkstemp(suffix=".mp3")

	ytdl = subprocess.Popen(["youtube-dl", arg, "--no-continue", "-f", "bestaudio", "--audio-format", "mp3", "-o", filename])
	while ytdl.poll() is None:
		await asyncio.sleep(1)

	# voice_data_wave = espeak.stdout.read()
	voice_data = discord.FFmpegOpusAudio(open(filename, "rb"), pipe=True)

	if ctx.message.guild.voice_client is not None and ctx.message.guild.voice_client.is_connected():
		voice_client = ctx.message.guild.voice_client
	else:
		voice_client = await voice_channel.connect()

	voice_client.play(voice_data)
	await ctx.message.add_reaction("✅")

