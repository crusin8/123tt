# TikTok Selenium Login Helper - Kullanım Kılavuzu

Bu araç, Selenium kullanarak TikTok'a otomatik olarak giriş yapmanızı ve gerekli token'ları (çerezleri) otomatik olarak almanızı sağlar. Bu sayede, TikTok API'sini kullanmak için gerekli token'ları manuel olarak çıkarma zahmetinden kurtulursunuz.

## Önkoşullar

Aracı kullanabilmek için aşağıdaki yazılımların kurulu olması gerekir:
- Python 3.6 veya üzeri
- Google Chrome tarayıcı
- Selenium ve Webdriver Manager Python kütüphaneleri:
  ```bash
  pip install selenium webdriver_manager
  ```

## Kullanım

Aracı kullanmak için aşağıdaki komutu çalıştırın:

```bash
python tiktok_selenium_login.py --username "TikTok_kullanici_adi" --password "TikTok_sifre"
```

### Parametreler

- `--username`: TikTok kullanıcı adınız veya e-posta adresiniz
- `--password`: TikTok şifreniz
- `--cookie-file`: Çerezleri kaydetmek için kullanılacak dosya adı (varsayılan: tiktok_cookies.json)
- `--env-file`: Oluşturulacak .env dosyasının adı (varsayılan: .env.selenium)
- `--keep-open`: İşlem tamamlandıktan sonra tarayıcıyı açık tut (varsayılan: kapalı)
- `--headless`: Tarayıcıyı görünmez şekilde çalıştır (CAPTCHA doğrulaması gerektiğinde sorun çıkarabilir, bu yüzden tavsiye edilmez)

## Örnek Kullanım Senaryoları

### 1. Temel Kullanım

```bash
python tiktok_selenium_login.py --username "kullanici_adi" --password "sifre"
```

Bu komut:
1. Chrome tarayıcısını açar
2. TikTok giriş sayfasına gider
3. Kullanıcı adı ve şifre ile giriş yapar
4. Gerekirse CAPTCHA doğrulaması için bekler
5. Giriş başarılı olduktan sonra:
   - Çerezleri tiktok_cookies.json dosyasına kaydeder
   - .env.selenium dosyasını oluşturur
6. İşlem tamamlandıktan sonra tarayıcıyı kapatır

### 2. Tarayıcıyı Açık Tutma (CAPTCHA Durumunda Yardımcı Olur)

```bash
python tiktok_selenium_login.py --username "kullanici_adi" --password "sifre" --keep-open
```

Bu komut, işlem tamamlandıktan sonra tarayıcıyı açık tutar. Bu, CAPTCHA doğrulaması gerektiğinde manuel olarak tamamlamanıza olanak tanır.

### 3. Özel Dosya İsimleri Kullanma

```bash
python tiktok_selenium_login.py --username "kullanici_adi" --password "sifre" --cookie-file "cerezlerim.json" --env-file ".env.tiktok"
```

Bu komut, çerezleri cerezlerim.json dosyasına kaydeder ve .env.tiktok adında bir .env dosyası oluşturur.

## CAPTCHA ve Doğrulama İşlemleri

TikTok, bot algılama mekanizmaları nedeniyle sık sık CAPTCHA veya diğer doğrulama işlemleri isteyebilir. Bu durumda:

1. Script, otomatik olarak 30 saniye bekleyecektir, bu süre içinde doğrulama işlemini manuel olarak tamamlayabilirsiniz.
2. `--keep-open` parametresini kullanarak tarayıcıyı açık tutabilir ve doğrulama işlemini rahatça yapabilirsiniz.
3. CAPTCHA işlemi tamamlandıktan sonra, script otomatik olarak devam eder ve token'ları kaydeder.

## Elde Edilen Token'ları Kullanma

İşlem başarılı olduktan sonra, script size token'ları nasıl kullanacağınızı gösteren bir komut örneği sunar:

```
python tiktok_reverse_api.py --env_file .env.selenium --video_id VIDEO_ID --comment "Yorumunuz"
```

Bu komutu kullanarak, TikTok API'sini otomatik olarak elde edilen token'lar ile kullanabilirsiniz.

## Sorun Giderme

1. **Giriş yapılamıyor**: TikTok'un giriş sayfası değişmiş olabilir. Kullanıcı adı ve şifre alanları için XPATH'leri güncellemek gerekebilir.

2. **CAPTCHA çözülemiyor**: `--keep-open` parametresini kullanarak tarayıcıyı açık tutun ve CAPTCHA'yı manuel olarak çözün.

3. **Token'lar alınamadı**: Giriş yaptıktan sonra bazı token'lar alınamadıysa, TikTok'un çerez yapısı değişmiş olabilir. Script'i güncellemek gerekebilir.

4. **"ChromeDriver başlatılamadı" hatası**: Chrome tarayıcınızın sürümü ile uyumlu bir ChromeDriver kurulu olmayabilir. webdriver_manager güncelleştirmeyi deneyin:
   ```bash
   pip install --upgrade webdriver_manager
   ```

## Güvenlik Notları

1. Bu script, kullanıcı adı ve şifrenizi komut satırından alır. Komut geçmişinde görünmesini istemiyorsanız, script'i interaktif olarak kullanabilirsiniz.
2. Şifreler komut satırı geçmişinde saklanabilir. Bu nedenle, paylaşılan bir bilgisayarda dikkatli olun.
3. Token'lar, TikTok hesabınıza erişim sağlayan önemli bilgilerdir. .env ve cookie dosyalarını güvenli tutun.

## Önemli Hatırlatma

TikTok, API'lerini izinsiz kullanılmasını engellemek için sürekli günceller. Bu script, TikTok tarafından tespit edilirse hesabınız kısıtlanabilir. Sadece kişisel kullanım içindir ve makul sıklıkta kullanılmalıdır. 