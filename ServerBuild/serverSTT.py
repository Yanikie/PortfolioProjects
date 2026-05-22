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

def loadModel():
    component = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("base", device= component)
    return model, component

def audioToWav(audioBytes, fileName):
    with wave.open(fileName, "wb") as wavFile:
        wavFile.setnchannels(1)
        wavFile.setsampwidth(2) # The data gets input as 16 bits so 2 bytes
        wavFile.setframerate(16000) # This sample rate is most used and already in use by esp
        wavFile.writeframes(audioBytes) # Write the data into wav file

def transcribe(bytes, model, component):
    text = ""
    # Before transcribing we need to have a wav file for Whisper
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as file:
        temporaryFileName = file.name
    
    try: 
        audioToWav(bytes,temporaryFileName)
        # It should transcribe the data we gave it. It should do it with no variation so temp = 0
        text = model.transcribe(temporaryFileName,fp16 = (component == "cuda"), temperature=0.0)
        return {"transcript": text["text"].strip(), "error": None}
    
    except Exception as errorCode: return {"transcript": None, "error": str(errorCode)}
    finally: os.unlink(temporaryFileName)

def handleClient(conn: socket.socket, model, component):
    # Read header data to find out how big audio chunk is going to be
    header = b""
    # Header is always 4 bytes
    while len(header) < 4:
        chunk = conn.recv(4 - len(header))
        if not chunk:
            return
        header += chunk
    # Take the header data from bytes to int value
    numBytes = struct.unpack("<I", header)[0]
    # Now for the audio
    audioBytes = b""
    while len(audioBytes) < numBytes:
        chunk = conn.recv(min(4096, numBytes - len(audioBytes)))
        # Last audio part has been found
        if not chunk:
            break
        audioBytes += chunk
    if len(audioBytes) < numBytes: return "Not all bytes received"    
    
    result = transcribe(audioBytes, model, component)

    response = json.dumps(result) + '\n'
    conn.sendall(response.encode("utf-8"))

    conn.close()

def main():
    model, component = loadModel()
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
            handleClient(connection, model, component)

if __name__ == "__main__":
    main()