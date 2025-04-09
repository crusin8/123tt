# TikTok Reverse Engineered API Bot

TikTok için doğrudan HTTP istekleriyle çalışan, reverse engineering mantığıyla geliştirilmiş bir API. Bu araç, TikTok hesabına giriş yaparak yorum gönderebilir, beğeni yapabilir ve kullanıcı takip edebilir.

## Özellikler

- TikTok API endpoint'lerini doğrudan kullanma (resmi olmayan)
- Video yorumu yapma
- Video beğenme
- Kullanıcı takip etme
- Tarayıcı çerezleri kullanarak kimlik doğrulama

## Kurulum

1. Repoyu klonlayın
2. Gerekli bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

## Kullanım

### 1. Gerekli Tokenların Alınması

TikTok API botunu kullanabilmek için öncelikle tarayıcınızdan bazı kimlik bilgilerini almanız gerekiyor. Bu kimlik bilgileri (token'lar) TikTok'a giriş yapmış bir tarayıcı oturumundan alınmalıdır.

Token'ları almanın en kolay yolu, tarayıcıdan çerezleri dışa aktarmak ve `get_tiktok_tokens.py` script'ini kullanmaktır:

```bash
python get_tiktok_tokens.py --cookie_file tiktok_cookies.json --output .env
```

Chrome'dan çerezleri dışa aktarmak için:
1. TikTok hesabınıza giriş yapın
2. Chrome DevTools'u açın (F12)
3. "Application" (Uygulama) sekmesine gidin
4. Sol tarafta "Storage" > "Cookies" > "https://www.tiktok.com" seçin
5. Sağ tıklayın ve "Save All as JSON" seçeneğini kullanarak çerezleri kaydedin

### 2. Bot'u Çalıştırma

Token'ları aldıktan sonra, reverse engineering API bot'unu çalıştırabilirsiniz:

```bash
python tiktok_reverse_api.py --video_id 7190527287440151814 --comment "Harika video!"
```

Veya `.env` dosyasını kullanarak:

```bash
python tiktok_reverse_api.py --env_file .env --video_id 7190527287440151814 --comment "Harika video!"
```

Video beğenmek için:
```bash
python tiktok_reverse_api.py --env_file .env --video_id 7190527287440151814 --like
```

Video sahibini takip etmek için:
```bash
python tiktok_reverse_api.py --env_file .env --video_id 7190527287440151814 --follow
```

Birden fazla işlemi aynı anda yapmak:
```bash
python tiktok_reverse_api.py --env_file .env --video_id 7190527287440151814 --comment "Harika!" --like --follow
```

### Parametreler

Bot için kullanabileceğiniz parametreler:

- `--session_id`: TikTok oturum kimliği (sessionid çerezi)
- `--ms_token`: TikTok ms_token değeri
- `--device_id`: TikTok cihaz ID'si (s_v_web_id çerezi)
- `--env_file`: Token'ların bulunduğu .env dosyasının yolu
- `--video_id`: Etkileşimde bulunulacak videonun ID'si
- `--comment`: Gönderilecek yorum metni
- `--like`: Videoyu beğen
- `--follow`: Video sahibini takip et

## Nasıl Çalışır?

Bu API, TikTok'un web sürümünün network isteklerini taklit ederek çalışır. Web uygulamasının kullandığı endpoint'leri ve istekleri analiz ederek:

1. Gerekli HTTP başlıklarını ve çerezleri ayarlar
2. İstek parametrelerini doğru formatta oluşturur
3. Doğrudan TikTok'un API endpoint'lerine HTTP istekleri gönderir

Bu yaklaşım sayesinde, herhangi bir tarayıcı otomasyonu veya üçüncü taraf kütüphane kullanmadan TikTok ile etkileşime geçebilirsiniz.

## Notlar ve Uyarılar

- Bu API, TikTok tarafından resmi olarak desteklenmemektedir ve reverse engineering yoluyla geliştirilmiştir.
- TikTok API'leri sık sık değiştiğinden, script'in çalışmasını durduracak güncellemeler olabilir.
- API çağrıları sınırlandırılabilir veya engelleme riski vardır.
- TikTok'un hizmet şartlarına aykırı kullanım olabileceğini unutmayın.
- Aşırı kullanım hesabınızın yasaklanmasına neden olabilir.

## Sorun Giderme

- Token'lar genellikle belirli bir süre sonra geçerliliğini yitirir. Botun çalışmayı durdurması durumunda, yeni token'lar almanız gerekebilir.
- "Login failed" hatası alırsanız, oturum token'larınızın süresi dolmuş demektir. Tarayıcıda tekrar giriş yapın ve yeni token'lar alın.
- "CSRF token not available" hatası için, tarayıcıda TikTok'a giriş yapıp token'ları yeniden alın.
- API sınırlamalarından kaçınmak için, bot'u çok sık çalıştırmaktan kaçının ve istekler arasında zaman bırakın. 