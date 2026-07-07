import json, urllib.request, websocket

def get_logs():
    try:
        req = urllib.request.urlopen("http://127.0.0.1:9222/json/list")
        targets = json.loads(req.read())
        target = next((t for t in targets if t.get('type') == 'page' and 'player_v2' in t.get('url', '')), None)
        
        if not target:
            print("No player_v2 tab found. Targets:")
            for t in targets: print(t.get('url'))
            return
            
        print(f"Attached to: {target['url']}")
        ws = websocket.create_connection(target['webSocketDebuggerUrl'])
        ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        
        ws.settimeout(3.0)
        while True:
            try:
                msg = json.loads(ws.recv())
                if msg.get("method") == "Runtime.consoleAPICalled":
                    args = msg["params"]["args"]
                    print("Console:", [a.get("value", a.get("description")) for a in args])
                elif msg.get("method") == "Runtime.exceptionThrown":
                    print("Exception:", msg["params"]["exceptionDetails"]["exception"]["description"])
            except websocket.TimeoutException:
                break
        ws.close()
    except Exception as e:
        print("Error:", e)

get_logs()
