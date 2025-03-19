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
import re
import soundfile as sf
from pydub import AudioSegment
load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")

if token is None:
    raise ValueError("DISCORD_BOT_TOKEN 環境變數未設置")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

keyword_dict = {
    "mvp": ["mvp"],
    "啊哈哈哈":["ahhaha"],
    "燒死你呀":["burn"],
    "躺贏狗":["dog"],
    "就解決你呀":["slove"],
    "嗚呼哈哈":["uhu"],
    "伊嗯嗯啊":["enn"],
    "啊嗨嗨":["ahihi"],
    "回答我":["answer"],
    "啊能能":["cancan"],
    "作業寫完了沒有":["homework"],
    "如此生活三十年":["living"],
    "look at my eyes":["look"],
    "啊嚕嚕嚕":["lulu"],
    "媽媽的味道":["mom"],
    "媽媽媽媽":["mommy"],
    "痛太痛啦":["pain"],
    " 說話":["speak"],
    "陽光青提":["sun"],
    "我們都在用力的活著":["working"],
    "豪赤":["yummy"],
}

config_dict = {
    "default": {
        "device": "cuda",
        "is_half": True,
        "t2s_weights_path": "models/gpt.ckpt",
        "vits_weights_path": "models/sovits.pth",
        "cnhuhbert_base_path": "models/chinese-hubert-base",
        "bert_base_path": "models/chinese-roberta-wwm-ext-large",
    }
}

tts_config = TTS_Config(config_dict)
tts_pipeline = TTS(tts_config)

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

def split_string_by_keywords(text, keyword_dict):
    # Split by dictionary keys (the keywords in the text)
    keywords = list(keyword_dict.keys())
    pattern = f"({'|'.join(map(re.escape, keywords))})"
    result = re.split(pattern, text, flags=re.UNICODE)
    
    # Map keywords to their replacement (first element of value list), keep non-keywords unchanged
    return [keyword_dict.get(s, s) for s in result if s.strip()]


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

def gpt_sovits(text: str, out_file):
    params = {
        "text": text,
        "text_lang": "zh",
        "ref_audio_path": "ref.wav",
        "top_k": 5,
        "text_split_method": "cut2",
    }

    sr, audio_data = next(tts_pipeline.run(params))
    sf.write(out_file, audio_data, sr)


@bot.tree.command(name="speak", description="讓Bot說話")
async def speak(interaction: discord.Interaction, text: str):
    await interaction.response.send_message("音訊正在生成中，請稍候...")
    await interaction.followup.send(text)
    loop = asyncio.get_event_loop()
    output = split_string_by_keywords(text, keyword_dict)
    combined = AudioSegment.empty()
    for idx, part in enumerate(output):
        # 如果為字串則使用 gpt_sovits 生成 wav
        if isinstance(part, str):
            temp_wav = os.path.join("temp_sounds", f"temp_{idx}.wav")
            await loop.run_in_executor(None, gpt_sovits, part, temp_wav)
    
            seg_audio = AudioSegment.from_file(temp_wav, format="wav")
            combined += seg_audio
        # 如果為列表則從 sounds 資料夾讀取對應的 wav
        elif isinstance(part, list):
            # 假設列表的第一個元素為檔名（不含副檔名）
            wav_path = os.path.join("sounds", f"{part[0]}.wav")
            seg_audio = AudioSegment.from_file(wav_path, format="wav")
            combined += seg_audio

    combined.export("final.wav", format="wav")
    
    if not bot.voice_clients:
        await interaction.followup.send(file=discord.File("final.wav"))
        return
    else:
        vc = bot.voice_clients[0]
        while vc.is_playing():
            await asyncio.sleep(0.1)
        vc.play(discord.FFmpegPCMAudio("final.wav"), after=lambda e: print(f"播放完成: {e}"))
        return

@bot.tree.command(name="download", description="下載生成的音訊文件")
async def download(interaction: discord.Interaction):
    if not os.path.exists("final.wav"):
        await interaction.response.send_message("音訊文件不存在")
        return

    await interaction.response.send_message(file=discord.File("final.wav"))

@bot.tree.command(name="list_keywords", description="列出所有關鍵字")
async def list_keywords(interaction: discord.Interaction):
    keywords = "\n".join(keyword_dict.keys())
    await interaction.response.send_message(f"關鍵字列表:\n{keywords}")

if __name__ == "__main__":
    bot.run(token)