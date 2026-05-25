#!/usr/bin/env python3
import socket # To host port
import struct # To unpack bytes into ints
import tempfile # To generate random new files which do not get overwritten
import wave # To write to a .wav file
import os # Unlinking temporary files
import torch # Checking if Cuda cores available
import whisper # The actual whisper model
import json # In order to talk to a model json text is preferred
import config
import requests
import numpy as np
import scipy.signal as signal

from kokoro import KPipeline


conversationHistory = []


# Loading transcription model
def loadModel():
    component = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("base", device= component)
    return model, component

# Loading TTS model
def loadTTSModel():return KPipeline(lang_code='a')

# Transfering the audio to a .wav file so whisper can analyse it
def audioToWav(audioBytes, fileName):
    with wave.open(fileName, "wb") as wavFile:
        wavFile.setnchannels(1)
        wavFile.setsampwidth(2) # The data gets input as 16 bits so 2 bytes
        wavFile.setframerate(16000) # This sample rate is most used and already in use by esp
        wavFile.writeframes(audioBytes) # Write the data into wav file

# Transcribing the audio we receive using the whisper model
def transcribe(audioBytes, model, component):
    # Before transcribing we need to have a wav file for Whisper
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as file: temporaryFileName = file.name
    try: 
        audioToWav(audioBytes,temporaryFileName)
        # It should transcribe the data we gave it. It should do it with no variation so temp = 0
        text = model.transcribe(temporaryFileName,language = "en", fp16 = (component == "cuda"), temperature=0.0)
        return {"transcript": text["text"].strip(), "error": None}
    
    except Exception as errorCode: return {"transcript": None, "error": str(errorCode)}
    finally: os.unlink(temporaryFileName)

# Send an api request to the ollama model hosted on port in config.py
def queryLLM(transcript):
    global conversationHistory
    conversationHistory.append({
        "role": "user",
        "content": transcript
    })
    payload = {
        "model": config.ollamaModel,
        "stream": False,
        "messages": [{"role": "system", "content": config.systemPrompt},
                    *conversationHistory]}

    try:
        # Use requests for ease of use and easy api querying
        resp = requests.post(
            f"{config.ollamaHost}/api/chat",
            json    = payload,
            timeout = 60
        )
        resp.raise_for_status()  # Error code from Ollama. Will be 4xx or 5xx code
        reply = resp.json()["message"]["content"].strip()
        conversationHistory.append({
            "role": "assistant",
            "content": reply
        })

        conversationHistory = conversationHistory[-12:]

        return {"reply": reply, "error": None}

    except requests.exceptions.Timeout:
        return {"reply": None, "error": "Ollama request timed out"}
    except requests.exceptions.ConnectionError:
        return {"reply": None, "error": "Could not connect to Ollama — is it running?"}
    except requests.exceptions.HTTPError as e:
        return {"reply": None, "error": f"Ollama HTTP error: {e}"}
    except Exception as e:
        return {"reply": None, "error": str(e)}

# Stream text to Kokoro
def streamKokoro(text, pipeline, conn: socket.socket):
    try:
        generator = pipeline(
            text,
            voice='af_heart',
            speed=1.0,
            split_pattern=r'\n+'
        )
        for _, _, audio in generator:
            # Convert float32 -> int16 PCM and from 24000 -> 16000
            audio = np.clip(audio, -1.0, 1.0)
            audio = signal.resample_poly(audio.cpu().numpy(), 2, 3)
            pcm = (audio * 32767).astype(np.int16)
            pcm_bytes = pcm.tobytes()
            # Send chunk size first then chunk
            conn.sendall(struct.pack("<I", len(pcm_bytes)))
            conn.sendall(pcm_bytes)

        # End marker
        conn.sendall(struct.pack("<I", 0))
        return {"error": None}
    except Exception as e:
        return {"error": str(e)}


def handleClient(conn: socket.socket, addr, model, device: str, pipeline):
    try:
        # Read the 4-byte header (same as before)
        header = b""
        while len(header) < 4:
            chunk = conn.recv(4 - len(header))
            if not chunk: return
            header += chunk

        num_bytes = struct.unpack("<I", header)[0] # Header tells how big
        max_bytes = 16000 * 2 * 30 # sample rate * width (amount of bytes) * maximum seconds

        if num_bytes == 0:
            conn.sendall(json.dumps({"transcript": None, "error": "empty audio"}).encode() + b"\n")
            return
        if num_bytes > max_bytes:
            conn.sendall(json.dumps({"transcript": None, "error": "audio too long"}).encode() + b"\n")
            return

        # Use an array to avoid copying when += 
        pcm = bytearray()
        while len(pcm) < num_bytes:
            to_read = min(4096, num_bytes - len(pcm)) # Read what has been sent
            chunk = conn.recv(to_read) # Gelezen deel
            if not chunk: break # Niks is stop
            
            pcm.extend(chunk) # Add chunk to array

        if len(pcm) < num_bytes:
            conn.sendall(json.dumps({"transcript": None, "error": "incomplete audio"}).encode() + b"\n")
            return
        # Start transcibing data when all audio is received
        print(f"    All audio received, transcribing...")
        result = transcribe(bytes(pcm), model, device)

        if result["error"]: print(f"[!] Transcription error: {result['error']}")

        else:
            print(f"    Transcript: {result['transcript']!r}")
            answerOfLLM = queryLLM(result['transcript'])

            # Print LLM response
            if answerOfLLM["error"]: print(f"[!] Ollama error: {answerOfLLM['error']}")
            else: print(f"    Ollama reply: {answerOfLLM['reply']!r}")
            
            # Format it as json
            response = json.dumps({
                "transcript": result["transcript"],
                "reply":      answerOfLLM["reply"],
                "error":      answerOfLLM["error"]
            }) + "\n"

        conn.sendall(response.encode("utf-8"))
        # TODO
        ttsResult = streamKokoro(answerOfLLM['reply'], pipeline, conn)
        if ttsResult['error']: print(f"[!] TTS error: {ttsResult['error']}")


    except Exception as e:
        print(f"[!] Unexpected error with {addr}: {e}")
        try:
            conn.sendall(json.dumps({"transcript": None, "error": str(e)}).encode() + b"\n")
        except Exception:
            pass
    finally:
        conn.close()
        print(f"[-] {addr} disconnected")

def main():
    model, component = loadModel()
    ttsModel = loadTTSModel()
    # Create a socket where tcp data can be transported to
    # AF_INET is ipv4 and SOCK_STREAM is TCP 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        # Try to minimise errror by releasing the port when the server restarts
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Now set to a specific address: Localhost: 5001
        srv.bind(("0.0.0.0", config.designatedPort))
        srv.listen(1)
        while True:
            # Block until connection has been made
            connection, address = srv.accept()
            handleClient(connection, address, model, component, ttsModel)

if __name__ == "__main__":
    main()