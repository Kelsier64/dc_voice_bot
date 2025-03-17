import discord
from discord.ext import commands, tasks
from discord.ui import Select, View
from dotenv import load_dotenv
import os
from datetime import datetime
import asyncio
from gtts import gTTS
import soundfile as sf
from gpt_sovits_python import TTS, TTS_Config
load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")

if token is None:
    raise ValueError("DISCORD_BOT_TOKEN1 環境變數未設置")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  # 同步指令
    command_count = len(bot.tree.get_commands())
    
    print(f"Bot is ready. 名稱 ---> {bot.user}")
    print(f"已載入 {command_count} 項指令")

@bot.event
async def on_disconnect():
    print("Bot is disconnected")

async def speak_text(text: str):
    if not bot.voice_clients:
        print("Bot 不在任何語音頻道中")
        return
    
    vc = bot.voice_clients[0]
    while vc.is_playing():
        await asyncio.sleep(0.1) 

    tts = gTTS(text, lang='zh')
    filename = "speech.mp3"
    tts.save(filename)

    vc.play(discord.FFmpegPCMAudio(filename), after=lambda e: print(f"播放完成: {e}"))


@bot.tree.command(name="join", description="加入語音頻道")
async def join(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message("你不在語音頻道中")
        return

    channel = interaction.user.voice.channel
    if bot.voice_clients:
        await bot.voice_clients[0].move_to(channel)
    else:
        await channel.connect()
    await interaction.response.send_message(f"已加入語音頻道: {channel.name}")

@bot.tree.command(name="leave", description="離開語音頻道")
async def leave(interaction: discord.Interaction):
    if not bot.voice_clients:
        await interaction.response.send_message("Bot 不在任何語音頻道中")
        return

    await bot.voice_clients[0].disconnect()
    await interaction.response.send_message("已離開語音頻道")

async def speak_text_gpt_sovits(text: str):
    print("gpt_sovits")
    if not bot.voice_clients:
        print("Bot 不在任何語音頻道中")
        return
    
    vc = bot.voice_clients[0]
    while vc.is_playing():
        await asyncio.sleep(0.1)

    config_dict = {
        "default": {
            "device": "cuda",
            "is_half": True,
            "t2s_weights_path": "/home/kelsier/py/dc_bot/models/gpt.ckpt",
            "vits_weights_path": "/home/kelsier/py/dc_bot/models/sovits.pth",
            "cnhuhbert_base_path": "/home/kelsier/py/dc_bot/models/chinese-hubert-base",
            "bert_base_path": "/home/kelsier/py/dc_bot/models/chinese-roberta-wwm-ext-large",
        }
    }
    
    tts_config = TTS_Config(config_dict)
    tts_pipeline = TTS(tts_config)

    params = {
        "text": text,
        "text_lang": "zh",
        "ref_audio_path": "/home/kelsier/py/dc_bot/ref.wav",
    }

    sr, audio_data = next(tts_pipeline.run(params))
    filename = "speech.wav"
    sf.write(filename, audio_data, sr)

    vc.play(discord.FFmpegPCMAudio(filename), after=lambda e: print(f"播放完成: {e}"))

@bot.tree.command(name="speak", description="讓Bot說話")
async def speak(interaction: discord.Interaction, text: str):
    if not bot.voice_clients:
        await interaction.response.send_message("Bot 不在任何語音頻道中")
        return
    await interaction.response.send_message("音訊正在生成中，請稍候...")
    await speak_text_gpt_sovits(text)
    await interaction.followup.send("播放完成")

@bot.tree.command(name="download", description="下載生成的音訊文件")
async def download(interaction: discord.Interaction):
    if not os.path.exists("speech.wav"):
        await interaction.response.send_message("音訊文件不存在")
        return

    await interaction.response.send_message(file=discord.File("speech.wav"))

async def main():
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())





