#!/usr/bin/env python3
"""
TikTok Selenium Login Helper

Bu script, Selenium kullanarak TikTok'a otomatik giriş yapar
ve giriş yaptıktan sonra çerezleri alıp kaydeder.
"""

import os
import json
import time
import argparse
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TikTokSeleniumLogin:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """Selenium web driver'ı yapılandır"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
            
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        # Mantıksız hataları engellemek için
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option("detach", True)
        
        # ChromeDriver kurulumu ve başlatılması
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logging.info("Chrome driver başarıyla başlatıldı")
        except Exception as e:
            logging.error(f"Chrome driver başlatılamadı: {str(e)}")
            raise
    
    def login(self, username, password):
        """TikTok'a giriş yapma"""
        try:
            logging.info("TikTok login sayfası açılıyor...")
            self.driver.get("https://www.tiktok.com/login/")
            
            # Giriş sayfasının yüklenmesini bekle
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'login-container')]"))
            )
            
            # Kullanıcı adı ve şifre giriş modunu seç
            logging.info("Kullanıcı adı ve şifre giriş modu seçiliyor...")
            try:
                # Kullanıcı adı/şifre seçeneğini bul ve tıkla
                login_with_email_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Email') or contains(text(), 'E-posta') or contains(text(), 'Use phone')]"))
                )
                login_with_email_button.click()
                time.sleep(1)
            except:
                logging.info("Kullanıcı adı/şifre giriş modu zaten aktif")
            
            # Kullanıcı adı ve şifre girişi
            logging.info("Kullanıcı adı ve şifre giriliyor...")
            
            # Kullanıcı adı/email alanı
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='username' or @name='email' or @placeholder='Email or username']"))
            )
            email_field.clear()
            email_field.send_keys(username)
            time.sleep(1)
            
            # Şifre alanı
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
            )
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Giriş butonuna tıkla
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            login_button.click()
            
            # Giriş başarılı mı kontrol et
            logging.info("Giriş yapılıyor, lütfen bekleyin...")
            
            # Doğrulama işlemi veya güvenlik kontrolü olabilir
            # Kullanıcının manuel müdahale edebilmesi için 30 saniye bekle
            time.sleep(15)
            
            # Ana sayfaya yönlendirildiyse başarılı
            if "tiktok.com/foryou" in self.driver.current_url or "tiktok.com/following" in self.driver.current_url:
                logging.info("Giriş başarılı! Ana sayfaya yönlendirildiniz.")
                return True
                
            # Profil sayfasına yönlendirilme durumu
            elif "tiktok.com/@" in self.driver.current_url:
                logging.info("Giriş başarılı! Profil sayfasına yönlendirildiniz.")
                return True
                
            # Hala giriş sayfasındaysak
            elif "tiktok.com/login" in self.driver.current_url:
                # CAPTCHA veya doğrulama gerekebilir, kullanıcıya bilgi ver
                logging.warning("Giriş sayfasında kaldınız. Muhtemelen CAPTCHA doğrulaması gerekiyor.")
                logging.warning("Lütfen tarayıcıda görünen doğrulama işlemlerini yapın.")
                
                # Kullanıcıya manüel işlem için daha fazla zaman tanı
                time.sleep(30)
                
                # Son kontrol
                if "tiktok.com/login" not in self.driver.current_url:
                    logging.info("Giriş başarılı! Doğrulama işleminden sonra yönlendirildiniz.")
                    return True
                else:
                    logging.error("Giriş başarısız. Doğrulama tamamlanamadı.")
                    return False
            else:
                logging.info(f"Bilinmeyen bir sayfaya yönlendirildiniz: {self.driver.current_url}")
                return False
            
        except Exception as e:
            logging.error(f"Giriş yapılırken hata oluştu: {str(e)}")
            return False
    
    def get_cookies(self):
        """Tarayıcı çerezlerini al"""
        try:
            cookies = self.driver.get_cookies()
            return cookies
        except Exception as e:
            logging.error(f"Çerezler alınırken hata oluştu: {str(e)}")
            return []
    
    def save_cookies(self, output_file="tiktok_cookies.json"):
        """Çerezleri dosyaya kaydet"""
        try:
            cookies = self.get_cookies()
            
            if not cookies:
                logging.error("Kaydedilecek çerez bulunamadı")
                return False
                
            with open(output_file, 'w') as f:
                json.dump(cookies, f, indent=4)
                
            logging.info(f"Çerezler başarıyla {output_file} dosyasına kaydedildi")
            return True
            
        except Exception as e:
            logging.error(f"Çerezler kaydedilirken hata oluştu: {str(e)}")
            return False
    
    def create_env_file(self, env_file=".env.selenium"):
        """Çerezlerden .env dosyası oluştur"""
        try:
            cookies = self.get_cookies()
            
            if not cookies:
                logging.error("Çerez bulunamadığı için .env dosyası oluşturulamadı")
                return False
            
            # Önemli çerezleri al
            cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
            
            # .env dosyasına yaz
            with open(env_file, "w") as f:
                f.write(f"# TikTok tokens - Otomatik oluşturuldu\n")
                
                if "sessionid" in cookie_dict:
                    f.write(f"TIKTOK_SESSION_ID={cookie_dict['sessionid']}\n")
                
                if "s_v_web_id" in cookie_dict:
                    f.write(f"TIKTOK_DEVICE_ID={cookie_dict['s_v_web_id']}\n")
                
                if "msToken" in cookie_dict:
                    f.write(f"TIKTOK_MS_TOKEN={cookie_dict['msToken']}\n")
                
                if "tt_csrf_token" in cookie_dict:
                    f.write(f"TIKTOK_CSRF_TOKEN={cookie_dict['tt_csrf_token']}\n")
                elif "passport_csrf_token" in cookie_dict:
                    f.write(f"TIKTOK_CSRF_TOKEN={cookie_dict['passport_csrf_token']}\n")
            
            logging.info(f".env dosyası başarıyla oluşturuldu: {env_file}")
            
            # Giriş için kullanılabilecek komut örneği göster
            logging.info("\nTikTok API'yı şu komutla kullanabilirsiniz:")
            logging.info(f"python tiktok_reverse_api.py --env_file {env_file} --video_id VIDEO_ID --comment \"Yorumunuz\"")
            
            return True
            
        except Exception as e:
            logging.error(f".env dosyası oluşturulurken hata oluştu: {str(e)}")
            return False
    
    def close(self):
        """Tarayıcıyı kapat"""
        if self.driver:
            self.driver.quit()
            logging.info("Tarayıcı kapatıldı")

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="TikTok'a Selenium ile giriş yap ve çerezleri kaydet")
    parser.add_argument("--username", required=True, help="TikTok kullanıcı adı veya email")
    parser.add_argument("--password", required=True, help="TikTok şifresi")
    parser.add_argument("--headless", action="store_true", help="Tarayıcıyı arka planda çalıştır (tavsiye edilmez)")
    parser.add_argument("--cookie-file", default="tiktok_cookies.json", help="Çerezlerin kaydedileceği dosya (default: tiktok_cookies.json)")
    parser.add_argument("--env-file", default=".env.selenium", help="Oluşturulacak .env dosyası (default: .env.selenium)")
    parser.add_argument("--keep-open", action="store_true", help="İşlem tamamlandıktan sonra tarayıcıyı açık tut")
    
    args = parser.parse_args()
    
    logging.info("TikTok Selenium Login Helper başlatılıyor...")
    
    # Headless modu için uyarı
    if args.headless:
        logging.warning("Headless mod kullanılıyor. CAPTCHA doğrulaması gerekirse bu işlem başarısız olabilir.")
    
    # Login işlemi
    tiktok_login = TikTokSeleniumLogin(headless=args.headless)
    
    try:
        if tiktok_login.login(args.username, args.password):
            # Giriş başarılı oldu, çerezleri kaydet
            tiktok_login.save_cookies(args.cookie_file)
            
            # .env dosyasını oluştur
            tiktok_login.create_env_file(args.env_file)
            
            logging.info("İşlem başarıyla tamamlandı!")
            
            # get_tiktok_tokens.py ile işlem
            try:
                logging.info("\nÇerezlerden token elde etme işlemi başlatılıyor...")
                os.system(f"python get_tiktok_tokens.py --cookie_file {args.cookie_file} --output {args.env_file}")
            except Exception as e:
                logging.error(f"get_tiktok_tokens.py çalıştırılırken hata: {str(e)}")
                
            if not args.keep_open:
                time.sleep(3)  # Sonuçları görebilmek için 3 saniye bekle
        else:
            logging.error("Giriş başarısız oldu.")
    except Exception as e:
        logging.error(f"İşlem sırasında hata oluştu: {str(e)}")
    finally:
        if not args.keep_open:
            tiktok_login.close()
        else:
            logging.info("Tarayıcı açık bırakıldı. Manuel olarak kapatabilirsiniz.")

if __name__ == "__main__":
    main() 