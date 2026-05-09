from fastapi import FastAPI, Form, HTTPException
import requests

app = FastAPI()

# Best practice: define URLs as variables
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"

@app.post("/summarize/")
def summarize(text: str = Form(...)):
    # 1. Error check: Empty Input
    if not text.strip():
        return {"summary": "Please enter some text to summarize."}

    # Prepare the payload for Ollama
    payload = {
        "model": "llama2",
        "prompt": f"Summarize this:\n\n{text}",
        "stream": False
    }

    print(f"\n--- DEBUG: Sending Request to Ollama ({OLLAMA_GENERATE_URL}) ---")
    print(f"Model: {payload['model']}")
    # print(f"Prompt length: {len(text)}") # Useful for very large inputs

    try:
        # 2. Improved request call with a timeout. Summarization takes time!
        response = requests.post(
            OLLAMA_GENERATE_URL,
            json=payload,
            timeout=180 # Give Ollama up to 3 minutes (180 seconds) to respond
        )
        
        # 3. Check HTTP Status Code from Ollama
        if response.status_code != 200:
            # If Ollama itself is failing (e.g., 404 or 500)
            print(f"DEBUG: Ollama returned HTTP error {response.status_code}")
            print(f"DEBUG: Ollama Error Body: {response.text}")
            raise HTTPException(status_code=500, detail=f"Ollama backend returned error: {response.status_code}")

        # 4. Safely try to parse JSON
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            print("DEBUG: Ollama returned invalid JSON (Response was not a proper dictionary).")
            print(f"DEBUG: Raw response: {response.text}")
            raise HTTPException(status_code=500, detail="Ollama returned corrupted data.")

        # --- VERY IMPORTANT DEBUGGING OUTPUT ---
        print("\n--- DEBUG FROM OLLAMA (JSON Dictionary) ---")
        print(f"Keys returned from Ollama: {list(result.keys())}")
        print(f"Complete dictionary: {result}")
        print("-------------------------------------------\n")

        # 5. Fix the KeyError: Use .get() instead of bracket syntax
        # result.get("response") returns None if the key is missing instead of crashing.
        summary_text = result.get("response")

        if summary_text is None:
            # Check if Ollama returned an explicit error dictionary
            error_msg = result.get("error")
            if error_msg:
                 return {"summary": f"Ollama Error: {error_msg} (Check if the 'llama2' model is pulled)."}
            else:
                 # Unexpected keys returned
                 return {"summary": "Error: Ollama did not generate a summary and gave no error message (unexpected response format)."}

        # Success: return the summary
        return {"summary": summary_text}

    except requests.exceptions.ConnectionError:
        print("DEBUG: Could not connect to Ollama (Is it running?).")
        raise HTTPException(status_code=500, detail="Backend failed to connect to Ollama (Is it running on 11434?).")
    except requests.exceptions.Timeout:
        print("DEBUG: The request to Ollama timed out (It took too long to think).")
        raise HTTPException(status_code=500, detail="Ollama took too long to respond.")
    except Exception as e:
        # Catch any other unexpected errors
        print(f"DEBUG: An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected backend error: {str(e)}")