<<<FILE: README.md>>>███████╗██╗██████╗ ███████╗ ██████╗ █████╗ ██████╗ 
██╔════╝██║██╔══██╗██╔════╝██╔════╝██╔══██╗██╔══██╗
███████╗██║██║  ██║█████╗  ██║     ███████║██████╔╝
╚════██║██║██║  ██║██╔══╝  ██║     ██╔══██║██╔══██╗
███████║██║██████╔╝███████╗╚██████╗██║  ██║██║  ██║
╚══════╝╚═╝╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝

     S T U D I O   E N G I N E   ×   P Y Q T 6
⚡ DOM Deep-Inspection · Regex Heuristics · Zero-Overhead AI PipelineGemini Web oturumundan doğrudan yerel geliştirme ortamına akıllı kod ayrıştırma ve senkronizasyon aracı.📖 İçindekilerGenel BakışTemel ÖzelliklerSistem Mimarisi ve Veri AkışıTeknik YığınDizin YapısıKurulum ve ÇalıştırmaKullanım SenaryolarıKamu Malı ve Özgürlük Bildirimi🌍 Genel BakışGemini Sidecar Studio, modern yapay zeka tabanlı kodlama akışlarında karşılaşılan "kopyala-yapıştır-dosyaya git-yaz" sürtünmesini tamamen ortadan kaldırmak üzere tasarlanmış yerel bir geliştirici arabirimidir[cite: 2].Uygulama, dahili bir QtWebEngine tarayıcı örneği üzerinden Gemini Web oturumunu barındırır[cite: 2]. Üretilen yanıtlar tek bir tuşla taranır, DOM hiyerarşisi derinlemesine incelenir (extractor_engine.py), kod parçalarının ait olduğu hedef dosya yolları tespit edilir ve tek tıkla yerel diske aktarılır[cite: 1, 2].⚡ Temel ÖzelliklerDOM Deep Inspector: ShadowRoot, iç içe iframe ve WebComponent yapılarını atlamayan özyinelemeli (recursive) DOM tarayıcı[cite: 1].Yol Çıkarım Sezgisi (Heuristics):Özel format direktifleri (<<<FILE: path/to/file>>>)[cite: 1]Kod bloğunun ilk satırlarındaki direktif ve yorum satırları (// path/to/file, # filepath: ...)[cite: 1]Kod bloklarının DOM başlıkları ve önceki paragraftaki inline referanslar[cite: 1]Dil sentaksına ve dosya içeriğine göre otomatik tahmin (package.json, tsconfig.json, Dockerfile, vb.)[cite: 1]Güven Skoru ve Doğrulama: Her çıkarılan dosya için %0 ile %100 arasında doğruluk güven skoru üretilir; staging tablosunda renk kodlarıyla listelenir[cite: 1, 2].Geri Al (Undo Stack): Diske yazılan dosyaların önceki sürümleri RAM üzerinde saklanır; 50 adıma kadar kayıpsız geri alma desteği sunar[cite: 2].Tek Tuşla Proje Hafızası: Tüm proje mimarisini ve kaynak kodları yapay zekanın anlayacağı markdown formatında tek tıkla panoya kopyalama[cite: 2].🏗️ Sistem Mimarisi ve Veri AkışıKod snippet'iflowchart LR
    A["🌐 Gemini Web UI<br/>(QtWebEngine)"] -->|"JS Injection<br/>(JS_DOM_DEEP_INSPECTOR)"| B["⚙️ Extractor Engine<br/>(extractor_engine.py)"]
    B -->|"Sentaks + Yol Sezgisi<br/>Güven Skoru Analizi"| C["📋 Staging Area<br/>(QTableWidget)"]
    C -->|"Kullanıcı Düzenleme / Onay"| D["💻 Kod Editörü<br/>(QPlainTextEdit)"]
    C -->|"Doğrudan Yazım"| E["💾 Yerel Disk<br/>(Project Root)"]
    D -->|"Kaydet"| E
    E -->|"Hafıza Çıkarımı"| F["🧠 LLM Context Memory<br/>(Panoya Kopyalama)"]
🛠️ Teknik YığınKatmanTeknolojiAçıklamaArayüz (GUI)PyQt6Masaüstü istemci arayüzü[cite: 2]Gömülü TarayıcıPyQt6-WebEngineChromium tabanlı izole web oturumu[cite: 2]Ayrıştırma ÇekirdeğiPython 3.10+ (Regex & Heuristics)Kod blokları ve dosya yolu yakalama motoru[cite: 1]Enjeksiyon ScriptiVanilla ES6+Shadow DOM ve iframe destekli DOM kazıyıcı[cite: 1]📂 Dizin YapısıPlaintext.
├── extractor_engine.py      # DOM denetçisi ve yol heuristiği motoru
├── gemini_sidecar.py        # PyQt6 arayüzü, editör ve dosya yöneticisi
├── .gitignore               # Sürüm kontrol dışı bırakılan dosyalar
└── README.md                # Dokümantasyon
💻 Kurulum ve ÇalıştırmaGereksinimlerPython 3.10 veya üzeripip paket yöneticisiAdımlarBash# 1. Depoyu klonlayın
git clone https://github.com/MuhammedCanCeylan/gemini-sidecar-studio.git
cd gemini-sidecar-studio

# 2. Sanal ortam oluşturun ve aktif edin
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Gerekli bağımlılıkları yükleyin
pip install PyQt6 PyQt6-WebEngine

# 4. Uygulamayı başlatın
python gemini_sidecar.py
⌨️ Temel Kısayollar ve İşlemlerButonİşlev⚡ Kodları AyrıştırWebEngine içindeki son yanıtı tarar ve Staging tablosuna aktarır[cite: 2].🚀 Ayrıştır ve Diske YazAyrıştırma işlemini yapar ve kullanıcı müdahalesi olmadan doğrudan diske kaydeder[cite: 2].🧠 Hafızayı KopyalaProje dizinindeki tüm desteklenen kaynak kodları tek bir LLM sistem promptu haline getirip panoya alır[cite: 2].⤺ Geri AlDosya üzerine yazılan son içeriği eski haline döndürür[cite: 2].📜 Kamu Malı ve Özgürlük BildirimiBu proje üzerinde hiçbir telif hakkı veya mülkiyet iddiası bulunmamaktadır. Yazılım kamu malına (Public Domain / The Unlicense) terk edilmiştir.This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.
Projeyi çatallayabilir (fork), parçalayabilir, baştan yazabilirsiniz.Ticari veya açık kaynaklı projelerinizin içine entegre edebilirsiniz.Herhangi bir atıfta bulunma, isim belirtme veya lisans metni ekleme zorunluluğu yoktur.İyileştirme yapmak, yeni motorlar/araçlar eklemek isteyen herkes dilediği gibi katkı sağlayabilir ve projeyi büyütebilir.<<<END_FILE>>>
