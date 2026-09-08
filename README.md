# Gemini Sidecar Studio

> **A starting point for building, experimenting, modifying, and creating something better.**

Gemini Sidecar Studio, Gemini Web'i bir masaüstü geliştirme ortamıyla birleştirmeyi amaçlayan deneysel bir **Project Architect / Code Intelligence** aracıdır.

Bu proje yalnızca ortaya çıkmış son bir ürün olarak değil, **üzerine yeni şeyler inşa edilebilecek bir başlangıç noktası** olarak düşünülmüştür.

Projenin amacı mükemmel veya tamamlanmış bir IDE sunmak değil; geliştiricilerin mevcut yapıyı inceleyerek kendi fikirlerini ekleyebileceği, sistemi değiştirebileceği ve çok daha ileri taşıyabileceği bir temel oluşturmaktır.

---

## 🚀 Project Philosophy

**Bu proje kapalı bir ürün olarak tasarlanmadı.**

Kodun nasıl çalıştığını inceleyebilir, istediğiniz bölümü değiştirebilir, kendi özelliklerinizi ekleyebilir veya projeyi tamamen farklı bir yöne taşıyabilirsiniz.

Bu repository'yi bir **başlangıç noktası** olarak kullanabilirsiniz.

Örneğin:

* Fork oluşturabilirsiniz.
* Kodu değiştirebilirsiniz.
* Yeni özellikler ekleyebilirsiniz.
* Mevcut sistemleri tamamen yeniden yazabilirsiniz.
* Kendi uygulamanızın temelini oluşturabilirsiniz.
* Kodun fikirlerinden ve mimarisinden yararlanabilirsiniz.
* Eğitim ve deney amaçlı kullanabilirsiniz.
* Kendi araçlarınızla birleştirebilirsiniz.
* Projeyi bambaşka bir ürüne dönüştürebilirsiniz.
* Başka geliştiricilerle birlikte geliştirebilirsiniz.

**Kısacası: Bu projeyi olduğu gibi kullanmak zorunda değilsiniz. Onu değiştirmek için buradasınız.**

---

## 🧠 What is Gemini Sidecar Studio?

Gemini Sidecar Studio, Gemini Web üzerinde gerçekleştirilen geliştirme süreçlerini masaüstü tarafındaki yardımcı araçlarla birleştiren bir deneysel çalışma alanıdır.

Proje temel olarak birkaç farklı bileşenin birlikte çalışması üzerine kuruludur:

```text
┌──────────────────────────────────────────────┐
│              Gemini Sidecar Studio           │
├──────────────────────────────────────────────┤
│                                              │
│  Gemini Web                                  │
│       │                                      │
│       ▼                                      │
│  WebEngine / Browser Layer                   │
│       │                                      │
│       ▼                                      │
│  DOM / Page Interaction                      │
│       │                                      │
│       ▼                                      │
│  Code Intelligence Engine                   │
│       │                                      │
│       ├── Code Extraction                    │
│       ├── Target Detection                   │
│       ├── File Mapping                       │
│       └── Project Analysis                   │
│                                              │
│       ▼                                      │
│  Project Architect                           │
│       │                                      │
│       ├── Project Explorer                   │
│       ├── Staging                            │
│       ├── File Writing                       │
│       └── Project Memory                     │
│                                              │
└──────────────────────────────────────────────┘
```

---

# ✨ Features

## 🌐 Gemini Web Integration

Proje, Gemini Web arayüzünü masaüstü uygulaması içerisinde çalıştırmak için Qt WebEngine tabanlı bir yapı kullanır.

Bu sayede Gemini ile yapılan etkileşimler, masaüstü tarafındaki proje araçlarıyla birlikte kullanılabilir.

---

## 🔍 Code Intelligence Engine

`extractor_engine.py`, web içerisindeki kod içeriklerini analiz etmek ve anlamlandırmak için çeşitli çıkarım mekanizmaları içerir.

Sistem:

* Kod bloklarını tespit etmeye,
* Dosya isimlerini belirlemeye,
* Proje yapısını anlamaya,
* Hedef dosyaları eşleştirmeye,
* Kod içeriklerini staging sürecine aktarmaya

çalışır.

Bu yapı özellikle daha gelişmiş otomatik proje yönetimi sistemleri için bir temel olarak kullanılabilir.

---

## 🏗️ Project Architect

`gemini_sidecar.py`, projenin masaüstü tarafındaki ana mimarisini oluşturur.

Project Architect yaklaşımı ile amaç yalnızca Gemini ile konuşmak değil, ortaya çıkan kodun gerçek bir proje yapısına dönüştürülmesini kolaylaştırmaktır.

Bunun içerisinde:

* Project Explorer
* Dosya yönetimi
* Kod staging
* Dosyaya yazma
* Proje ağacı oluşturma
* Proje hafızası
* Kod çıkarma
* Web içerik analizi

gibi bileşenler bulunur.

---

## 📂 Project Explorer

Projelerin dosya yapısını masaüstü üzerinden görüntülemek ve yönetmek için kullanılan bir explorer yapısı bulunur.

Bu yapı daha sonra:

* IDE özellikleri,
* Git entegrasyonu,
* Diff görüntüleme,
* Dosya karşılaştırma,
* Proje arama,
* Otomatik refactoring

gibi özelliklerle geliştirilebilir.

---

## 🧩 Code Extraction

Gemini tarafından oluşturulan veya web sayfasında bulunan kodların algılanması ve proje içerisinde kullanılabilecek hale getirilmesi projenin temel fikirlerinden biridir.

Örneğin:

```text
Gemini Response
      │
      ▼
Code Detection
      │
      ▼
Filename Detection
      │
      ▼
Target Resolution
      │
      ▼
Staging
      │
      ▼
Project Files
```

Bu sistemin çok daha ileri seviyeye taşınması mümkündür.

---

# 🛠️ Technology

Proje temel olarak şu teknolojiler üzerine kuruludur:

* Python
* PyQt6
* Qt WebEngine
* JavaScript
* HTML
* CSS
* Gemini Web
* Regex / Text Analysis
* File System APIs

---

# 📁 Project Structure

```text
gemini-sidecar-studio/
│
├── gemini_sidecar.py
│
├── extractor_engine.py
│
├── .gitignore
│
└── README.md
```

### `gemini_sidecar.py`

Masaüstü uygulamasının ana tarafıdır.

WebEngine, Gemini Web entegrasyonu, Project Architect, proje yönetimi ve dosya işlemleri gibi bölümleri barındırır.

### `extractor_engine.py`

Kod çıkarma ve hedef çözümleme işlemlerinden sorumlu olan intelligence katmanıdır.

---

# ⚙️ Getting Started

## Requirements

Python 3.x ve gerekli Python paketleri.

Projeyi klonlayın:

```bash
git clone https://github.com/MuhammedCanCeylan/gemini-sidecar-studio.git
cd gemini-sidecar-studio
```

Gerekli paketleri yükleyin:

```bash
pip install PyQt6 PyQt6-WebEngine
```

Ardından:

```bash
python gemini_sidecar.py
```

---

# 🧪 Experimental Project

Bu repository'nin önemli bir özelliği, **tamamlanmış bir ürün olma iddiasında bulunmamasıdır.**

Bazı sistemler deneysel olabilir.

Bazı özellikler geliştirilmeye ihtiyaç duyabilir.

Bazı mimari kararlar ileride tamamen değiştirilebilir.

Bu bilinçli bir tercihtir.

Çünkü bu repository'nin amacı yalnızca mevcut kodu korumak değil, **yeni fikirlerin üzerine inşa edilebileceği bir alan oluşturmak**tır.

---

# 🤝 Build Something Better

Bu projeyi kullanıyorsanız, mevcut yapıya bağlı kalmak zorunda değilsiniz.

Kodun herhangi bir bölümünü:

```text
anla
 ↓
değiştir
 ↓
geliştir
 ↓
yeniden tasarla
 ↓
kendi fikrini ekle
```

şeklinde ele alabilirsiniz.

Bir özelliği tamamen silmek istiyorsanız silebilirsiniz.

Bir sistemi baştan yazmak istiyorsanız yazabilirsiniz.

Daha iyi bir mimari fikriniz varsa mevcut mimariyi değiştirebilirsiniz.

Projeyi başka bir teknolojiye taşımak istiyorsanız taşıyabilirsiniz.

**Bu repository'nin değeri, olduğu haliyle kalmasından değil, insanların onu alıp daha ileri götürmesinden gelir.**

---

# 🌱 A Starting Point

Gemini Sidecar Studio'yu bir **final product** olarak değil, bir **starting point** olarak düşünün.

Belki buradaki fikirleri kullanarak daha iyi bir IDE yapacaksınız.

Belki Gemini için tamamen farklı bir desktop environment geliştireceksiniz.

Belki sadece `extractor_engine.py` içerisindeki fikirleri alıp başka bir projede kullanacaksınız.

Belki de bu repository'yi fork'layıp bambaşka bir projeye dönüştüreceksiniz.

Hepsi bu projenin amaçladığı kullanım şekilleridir.

---

# ❤️ Use It. Change It. Build On It.

Bu repository üzerinde **hak iddia eden kapalı bir ürün anlayışı oluşturmak istemiyorum.**

Bu kodu bir başlangıç noktası olarak paylaşıyorum.

**İstediğiniz gibi kullanın.
Değiştirin.
Geliştirin.
Fork'layın.
Kendi projelerinize uyarlayın.
Üzerine yeni şeyler inşa edin.**

Projeyi daha iyi hale getirirseniz harika.

Tamamen farklı bir şeye dönüştürürseniz de harika.

Buradaki fikirlerden ilham alıp kendi sisteminizi geliştirirseniz, bu repository'nin amacına ulaşmış demektir.

> **Don't just use the project. Build on it.**

---

# 📌 Final Note

Bu proje bir son nokta değildir.

**Bir başlangıç noktasıdır.**

Kod burada duruyor.

Sıradaki adım size ait.

**Take it. Break it. Improve it. Rebuild it.**

---

<p align="center">
  <b>Gemini Sidecar Studio</b><br>
  A starting point for the next idea.
</p>
