import sys

def main():
    log_path = r"c:\Users\ASUS\Documents\PTIT\DOAN\HQTCSDL\logs\24-06-26\api_log.txt"
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        post_logs = []
        for line in lines:
            if "POST" in line or "login" in line:
                if "/user/login" in line and " - {} - " in line:
                    post_logs.append(line.strip())
        
        print("--- LAST 10 LOGIN POST LOGS (JUNE 24) ---")
        for log in post_logs[-10:]:
            print(log)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
