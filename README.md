# TikTok Reverse Engineered API Bot

TikTok için doğrudan HTTP istekleriyle çalışan, reverse engineering mantığıyla geliştirilmiş bir API. Bu araç, TikTok hesabına giriş yaparak yorum gönderebilir, beğeni yapabilir ve kullanıcı takip edebilir.

## Özellikler

- TikTok API endpoint'lerini doğrudan kullanma (resmi olmayan)
- Video yorumu yapma
- Video beğenme
- Kullanıcı takip etme
- Kullanıcı adı ve şifre ile doğrudan giriş yapma (Web ve Mobil API destekli)
- Tarayıcı çerezleri kullanarak kimlik doğrulama

## Kurulum

1. Repoyu klonlayın
2. Gerekli bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

## Kullanım

### 1. Giriş Yapma

TikTok API botunu kullanmak için iki farklı yöntemle giriş yapabilirsiniz:

#### A. Doğrudan Kullanıcı Adı ve Şifre ile Giriş (Güncellendi)

Doğrudan kullanıcı adı ve şifre ile giriş yapabilirsiniz. Güncellenmiş API, birden fazla giriş yöntemini otomatik olarak dener:

```bash
python tiktok_reverse_api.py --username "kullaniciadi" --password "şifre" --video_id 7190527287440151814 --comment "Harika video!"
```

Bu yöntem, tarayıcıdan token almanıza gerek kalmadan API'yi kullanmanızı sağlar ve aşağıdaki yöntemleri otomatik olarak dener:
1. TikTok Web Passport API
2. TikTok SSO API
3. TikTok Mobil API

#### B. Tarayıcı Token'ları ile Giriş

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
python tiktok_reverse_api.py --username "kullaniciadi" --password "şifre" --video_id 7190527287440151814 --like
```

Video sahibini takip etmek için:
```bash
python tiktok_reverse_api.py --username "kullaniciadi" --password "şifre" --video_id 7190527287440151814 --follow
```

Birden fazla işlemi aynı anda yapmak:
```bash
python tiktok_reverse_api.py --username "kullaniciadi" --password "şifre" --video_id 7190527287440151814 --comment "Harika!" --like --follow
```

### Doğrudan Giriş Testi

#### Genel Giriş Testi

Doğrudan giriş işlevini test etmek için:

```bash
python test_login.py --username "kullaniciadi" --password "şifre" --save_tokens --test_api --video_id 7190527287440151814
```

Bu komut:
- Kullanıcı adı ve şifre ile giriş yapacak
- Elde edilen token'ları `.env.login` dosyasına kaydedecek
- API işlevlerini test edecek ve belirtilen video hakkında bilgi alacak

#### Gelişmiş API Giriş Testi (Yeni)

TikTok API giriş sorunlarını gidermek için özel bir test aracı:

```bash
python test_login_fix.py --username "kullaniciadi" --password "şifre" --method all
```

Bu komut aşağıdaki giriş yöntemlerini test eder:
- `--method direct`: Web API passport endpoint'ini kullanarak giriş
- `--method sso`: TikTok SSO endpoint'ini kullanarak giriş
- `--method mobile`: Mobil API endpoint'ini kullanarak giriş
- `--method all`: Tüm yöntemleri sırayla dener (varsayılan)

Her giriş denemesi ayrıntılı günlük kaydı ile `tiktok_login_fix.log` dosyasına kaydedilir.

### Parametreler

Bot için kullanabileceğiniz parametreler:

#### Token-based Authentication
- `--session_id`: TikTok oturum kimliği (sessionid çerezi)
- `--ms_token`: TikTok ms_token değeri
- `--device_id`: TikTok cihaz ID'si (s_v_web_id çerezi)
- `--env_file`: Token'ların bulunduğu .env dosyasının yolu

#### Direct Login
- `--username`: TikTok kullanıcı adı veya email
- `--password`: TikTok şifresi

#### Actions
- `--video_id`: Etkileşimde bulunulacak videonun ID'si
- `--comment`: Gönderilecek yorum metni
- `--like`: Videoyu beğen
- `--follow`: Video sahibini takip et

## Güncellemeler (Yeni)

### API login sorunları için çözüm (9 Nisan 2024)

- `"url doesn't match"` hatası için TikTok giriş API endpoint'leri güncellendi
- Çoklu giriş yöntemi desteği eklendi (Web Passport, SSO ve Mobil API)
- Test araçları ve detaylı hata ayıklama günlükleri eklendi
- Token yönetimi ve MS Token oluşturma mekanizması iyileştirildi
- Mobil API desteği eklendi (daha kararlı giriş yöntemi)

## Nasıl Çalışır?

Bu API, TikTok'un web sürümünün network isteklerini taklit ederek çalışır. Web uygulamasının kullandığı endpoint'leri ve istekleri analiz ederek:

1. Kullanıcı adı ve şifre ile doğrudan giriş yapar veya gerekli HTTP başlıklarını ve çerezleri ayarlar
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

- Doğrudan giriş ile ilgili sorunlarda, `test_login_fix.py` scriptini kullanarak hangi giriş yönteminin çalıştığını tespit edin
- `"url doesn't match"` hatası alırsanız, sistem otomatik olarak alternatif giriş yöntemlerini deneyecektir.
- Doğrudan giriş ile ilgili sorunlarda, TikTok'un CAPTCHA veya diğer güvenlik önlemlerini etkinleştirmiş olabileceğini unutmayın.
- Token'lar genellikle belirli bir süre sonra geçerliliğini yitirir. Botun çalışmayı durdurması durumunda, yeni token'lar almanız gerekebilir.
- "Login failed" hatası alırsanız, oturum token'larınızın süresi dolmuş demektir. Tarayıcıda tekrar giriş yapın ve yeni token'lar alın.
- "CSRF token not available" hatası için, tarayıcıda TikTok'a giriş yapıp token'ları yeniden alın.
- API sınırlamalarından kaçınmak için, bot'u çok sık çalıştırmaktan kaçının ve istekler arasında zaman bırakın. 