import discord
import os
import math
import json
import uuid
import asyncio
import time
import paramiko

async def send_file_to_discord(channel, file_path, uuid):
    try:
        return await channel.send(f"Posted via GPT-4 OpenAI. UUID File: {uuid}", file=discord.File(file_path))
    except Exception as e:
        print(f"An error occurred while sending the file to the Server: {e}")
        return None

async def split_and_send_file(channel, file_path, chunk_size):
    try:
        file_name, file_extension = os.path.splitext(file_path)
        unique_id = str(uuid.uuid4())

        file_size = os.path.getsize(file_path)
        sent_bytes = 0
        start_time = time.time()

        chunks_info = {}

        if os.path.exists('files.json'):
            with open('files.json', 'r') as json_file:
                chunks_info = json.load(json_file)

        if unique_id not in chunks_info:
            chunks_info[unique_id] = {"file_name": f"{file_name}{file_extension}", "parts": []}

        if file_size <= (10 * 1024 * 1024):
            message = await send_file_to_discord(channel, file_path, unique_id)
            end_time = time.time()
            time_taken = end_time - start_time
            mb_sent = file_size / (1024 * 1024)
            speed = mb_sent / time_taken if time_taken != 0 else 0

            if message is not None:
                print(f"The file {file_path} has been sent to the server.")
            else:
                print(f"Unable to obtain message ID for file {file_path}")

            return

        temp_folder = 'temp'

        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        with open(file_path, 'rb') as file:
            for i in range(math.ceil(file_size / chunk_size)):
                chunk_data = file.read(chunk_size)
                chunk_id = str(i + 1)
                chunk_file_name = f"{file_name}_{unique_id}_part{chunk_id}{file_extension}"
                sent_bytes += len(chunk_data)

                with open(os.path.join(temp_folder, chunk_file_name), 'wb') as chunk_file:
                    chunk_file.write(chunk_data)

                message = await send_file_to_discord(channel, os.path.join(temp_folder, chunk_file_name), unique_id)

                if message is not None:
                    start = i * chunk_size
                    end = min((i + 1) * chunk_size, file_size)
                    chunks_info[unique_id]["parts"].append({
                        "file_name": chunk_file_name,
                        "id": unique_id,
                        "normal": f"{file_name}{file_extension}",
                        "message_id": message.id,
                        "start": start,
                        "end": end
                    })

                    with open('files.json', 'w') as json_file:
                        json.dump(chunks_info, json_file, indent=4, ensure_ascii=False)

                    percent_complete = (sent_bytes / file_size) * 100
                    time_taken = time.time() - start_time
                    speed = sent_bytes / (1024 * 1024 * time_taken) if time_taken != 0 else 0

                    print(f"Progress: {percent_complete:.2f}% | Speed: {speed:.2f} MB/s")

        for part in chunks_info[unique_id]["parts"]:
            file_path = os.path.join(temp_folder, part["file_name"])
            if os.path.exists(file_path):
                os.remove(file_path)

        print(f"The file {file_name} has been successfully sent to the server. You will find the file ID in files.json.")
        
        upload_to_sftp(chunks_info)
    except Exception as e:
        print(f"Error: {e}")

def upload_to_sftp(data):
    try:
        host = 'ip'
        username = 'user'
        password = 'pass'

        transport = paramiko.Transport((host, 22))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        files = sftp.listdir('.')
        file_exists = 'files.json' in files

        if file_exists:
            with sftp.file('files.json', 'r') as file:
                existing_data = json.load(file)

            existing_data.update(data)

            with sftp.file('files.json', 'w') as file:
                json.dump(existing_data, file, indent=4, ensure_ascii=False)

        else:
            with sftp.file('files.json', 'w') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        sftp.close()
        transport.close()
        print("SFTP connection successful.")
    except Exception as e:
        print(f"SFTP connection failed: {e}")

if __name__ == "__main__":
    TOKEN = "discord_bot_token"
    CHANNEL_ID = CHANNEL_ID  
    file_to_split = input("Enter the file name for upload (minimum 5MB. Not the file path, just the name: ")
    chunk_size_bytes = 5 * 1024 * 1024

    if not os.path.exists('temp'):
        os.makedirs('temp')

    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        channel = client.get_channel(CHANNEL_ID)
        await split_and_send_file(channel, file_to_split, chunk_size_bytes)
        await asyncio.sleep(5)
        await client.close()

    client.run(TOKEN)
