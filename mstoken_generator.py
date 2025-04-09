import time
import random
import string
import hashlib
import base64
import hmac
import json
import argparse

def generate_device_fingerprint():
    """
    Rastgele bir cihaz parmak izi oluşturur
    """
    # Tipik olarak birçok cihaz parametresi göz önünde bulundurulur
    device_info = {
        "browser": "Chrome",
        "browser_version": "120.0.6099.130",
        "os": "Mac OS",
        "screen_width": 1920,
        "screen_height": 1080,
        "timezone": "Europe/Istanbul",
        "language": "tr-TR",
        "platform": "MacIntel",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Hash cihaz bilgilerini
    device_string = json.dumps(device_info, sort_keys=True)
    fingerprint = hashlib.sha256(device_string.encode()).hexdigest()
    return fingerprint

def generate_ms_token(session_id=None, csrf_token=None):
    """
    Tiktok'un msToken değerini üretmeye çalışır. Bu gerçek algoritmanın basitleştirilmiş bir taklididir.
    
    Gerçek algoritma daha karmaşıktır ve tarayıcı davranışının, tarayıcı parmak izinin, 
    oturum durumunun ve TikTok'un iç kodlamasının bir kombinasyonunu içerir.
    """
    timestamp = int(time.time() * 1000)  # milisaniye cinsinden zaman damgası
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    # Bazı girdiler
    device_fp = generate_device_fingerprint()
    timestamp_str = str(timestamp)
    
    # Oturum kimliği ve CSRF token'ı kullanarak bir "seed" oluşturalım
    seed = timestamp_str
    if session_id:
        seed += session_id
    if csrf_token:
        seed += csrf_token
    
    # HMAC ile imzalama (bu gerçek TikTok'un kullandığı algoritma değil, sadece bir örnek)
    h = hmac.new(device_fp.encode(), seed.encode(), hashlib.sha256)
    signature = h.digest()
    
    # Base64 kodlama ve işleme
    b64_sig = base64.b64encode(signature).decode('utf-8')
    b64_sig = b64_sig.replace('+', '-').replace('/', '_').replace('=', '')
    
    # Rastgele bileşenleri karıştırma
    ms_token_parts = [
        b64_sig[:12],                        # İmzadan bir parça
        random_part,                         # Rastgele kısım
        timestamp_str[-4:],                  # Zaman damgasının son 4 hanesi
        device_fp[:8]                        # Cihaz parmak izinin bir kısmı
    ]
    
    # Parçaları birleştirme ve işleme
    ms_token = ''.join(ms_token_parts)
    
    # Son işleme (yeterli uzunlukta değilse ayarlama)
    if len(ms_token) < 128:
        padding = ''.join(random.choices(string.ascii_letters + string.digits, k=128-len(ms_token)))
        ms_token += padding
    
    # Gerçek msToken değerlerinin tipik uzunluğu ~140-160 karakter arasıdır
    return ms_token[:150]

def main():
    parser = argparse.ArgumentParser(description='Generate TikTok msToken')
    parser.add_argument('--session_id', help='TikTok session ID')
    parser.add_argument('--csrf_token', help='TikTok CSRF token')
    parser.add_argument('--count', type=int, default=3, help='Number of tokens to generate')
    
    args = parser.parse_args()
    
    print(f"\nGenerating {args.count} msToken samples:")
    print("-" * 50)
    
    for i in range(args.count):
        token = generate_ms_token(args.session_id, args.csrf_token)
        print(f"Sample {i+1}: {token}")
    
    print("-" * 50)
    print("NOT: Bu tokenler gerçek TikTok algoritmasına dayalı değil, sadece benzer yapıda örneklerdir.")
    print("Gerçek msToken algoritması daha karmaşıktır ve tarayıcı ortamı içinde JavaScript tarafından üretilir.")
    print("Bu tokenleri kullanmaya çalıştığınızda TikTok API'si hata verebilir.")

if __name__ == "__main__":
    main() 