````md
# Laporan Proyek UAS  
## Sistem Terdistribusi dan Paralel A  
### Pub-Sub Idempotent Log Aggregator

---

**Nama** : Muhammad Azka Yunastio  
**NIM** : 11231036  
**Mata Kuliah** : Sistem Terdistribusi dan Paralel A  

**Repository** : (opsional)  
**Link Video Demo** : (isi link YouTube jika diminta)

---

## 1. Pendahuluan

Perkembangan sistem terdistribusi modern menuntut kemampuan untuk memproses data secara **paralel, toleran terhadap kegagalan, dan konsisten secara logis** meskipun berada dalam kondisi konkurensi tinggi. Salah satu permasalahan umum adalah **duplikasi event**, **reordering pesan**, serta **kegagalan parsial** pada worker atau jaringan.

Proyek UAS ini mengimplementasikan sebuah **Pub-Sub Log Aggregator** yang dirancang untuk:

- menerima event dalam jumlah besar,
- memproses event secara paralel,
- menjamin **idempotency** dan **exactly-once semantics secara logis**,
- tetap konsisten pada kondisi konkurensi tinggi,
- serta tahan terhadap restart dan kegagalan container.

Sistem dibangun mengikuti prinsip-prinsip dalam *Distributed Systems: Concepts and Design* (Coulouris et al., 2012), khususnya pada topik **Indirect Communication, Failure Handling, Transactions, dan Concurrency Control**.

---

## 2. Gambaran Umum Arsitektur Sistem

### 2.1 Model Arsitektur

Sistem menggunakan **arsitektur Publish–Subscribe** dengan pendekatan *microservices* yang dijalankan menggunakan **Docker Compose**.

Alur data secara umum:

1. **Publisher** mengirim event ke endpoint `/publish`
2. **Aggregator (FastAPI)**:
   - memvalidasi skema event
   - memasukkan event ke storage
   - melakukan deduplikasi berbasis `event_id`
3. **Worker background** memproses event secara paralel
4. **Database PostgreSQL** menyimpan data persisten
5. **Endpoint `/stats`** menyajikan metrik sistem

Arsitektur ini memisahkan:
- produsen data (publisher),
- pemroses data (aggregator + worker),
- dan penyimpanan data (PostgreSQL),

sehingga tercapai **loose coupling** dan **skalabilitas horizontal**.

---

## 3. Struktur File Proyek

Berikut adalah struktur direktori proyek **Pub-Sub Log Aggregator** beserta penjelasan peran masing-masing file. Struktur ini mencerminkan pemisahan tanggung jawab (*separation of concerns*) antara layanan, pengujian, dan infrastruktur.

UAS/
├── aggregator/
│   ├── **init**.py
│   ├── main.py
│   ├── models.py
│   ├── db.py
│   ├── worker.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── publisher/
│   ├── **init**.py
│   ├── main.py
│   ├── generator.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── db/
│   └── init.sql
│
├── docs/
│   └── schema.sql
│
├── k6/
│   └── publish.js
│
├── tests/
│   ├── **init**.py
│   ├── test_01_schema_validation.py
│   ├── test_02_dedup_basic.py
│   ├── test_03_batch_atomic.py
│   ├── test_04_stats_consistency.py
│   ├── test_05_persistence_restart.py
│   ├── test_06_concurrency_upsert.py
│   ├── test_07_ordering_and_timestamp.py
│   ├── test_08_invalid_payload.py
│   ├── test_09_large_payload.py
│   ├── test_10_health_and_observability.py
│   ├── test_11_single_event_insert.py
│   ├── test_12_partial_batch_rollback.py
│   ├── test_13_same_event_id_different_topic.py
│   ├── test_14_stats_under_concurrency.py
│   ├── test_15_high_frequency_duplicates.py
│   ├── test_16_limit_parameter.py
│   ├── test_17_topic_filtering.py
│   ├── test_18_list_not_empty.py
│   ├── test_19_stats_keys_exist.py
│   └── test_20_stats_endpoint_stable.py
│
├── docker-compose.yml
├── README.md
├── report.md
├── theory.md
├── .env.example
└── .gitignore

---

### 3.1 Direktori `aggregator/`

Merupakan inti sistem.

| File | Fungsi |
|---|---|
| `main.py` | Entry point FastAPI, routing endpoint |
| `models.py` | Validasi skema event (Pydantic) |
| `db.py` | Logika transaksi database dan upsert |
| `worker.py` | Background worker pemroses event |
| `Dockerfile` | Containerisasi layanan aggregator |

Aggregator bertanggung jawab atas:
- validasi data,
- kontrol transaksi,
- deduplikasi event,
- penghitungan statistik sistem.

---

### 3.2 Direktori `publisher/`

Berfungsi sebagai **event simulator**.

| File | Fungsi |
|---|---|
| `generator.py` | Generator event uji |
| `main.py` | Pengiriman event ke aggregator |
| `Dockerfile` | Container publisher |

Digunakan untuk:
- pengujian fungsional,
- simulasi event burst,
- integrasi dengan k6.

---

### 3.3 Database (`db/` dan `docs/`)

| File | Fungsi |
|---|---|
| `schema.sql` | Definisi tabel dan constraint |
| `init.sql` | Inisialisasi database |

Skema database menggunakan:
- **primary key & unique constraint pada `event_id`**
- **transaction-safe insert**
- **durable storage melalui Docker volume**

---

### 3.4 Pengujian Beban (`k6/`)

| File | Fungsi |
|---|---|
| `publish.js` | Load testing ≥ 20.000 event |

k6 digunakan untuk:
- menguji sistem pada kondisi **high concurrency**
- mensimulasikan duplikasi event masif
- memverifikasi konsistensi statistik

---

## 4. Keputusan Desain Sistem

### 4.1 Idempotency & Deduplication

Sistem mengimplementasikan pola **Idempotent Consumer**.

- Setiap event memiliki `event_id` unik
- Database menggunakan:
  ```sql
  INSERT ... ON CONFLICT (event_id) DO NOTHING
````

* Event duplikat **tidak memodifikasi state sistem**

Dengan pendekatan ini:

* sistem dapat menerima **at-least-once delivery**
* namun menghasilkan **exactly-once semantics secara logis**

Ini adalah solusi praktis terhadap keterbatasan sistem terdistribusi yang tidak dapat menjamin pengiriman tunggal tanpa koordinasi mahal.

---

### 4.2 Transaksi & Kontrol Konkurensi (Bab 8–9)

Setiap operasi penulisan event dibungkus dalam **transaksi database lokal** yang memenuhi sifat **ACID**:

* **Atomicity**: event + statistik ditulis bersama
* **Consistency**: constraint database dijaga
* **Isolation**: konkurensi worker tidak menyebabkan lost update
* **Durability**: data bertahan setelah crash

Alih-alih menggunakan locking eksplisit, sistem mengandalkan:

* **unique constraint**
* **atomic upsert**
* **optimistic concurrency**

Pendekatan ini terbukti lebih **scalable** dan **deadlock-free**.

---

### 4.3 Persistensi & Toleransi Kegagalan (Bab 6)

Sistem mendukung toleransi kegagalan melalui:

* **Docker Named Volume** untuk PostgreSQL
* kemampuan restart container tanpa kehilangan data
* retry mekanisme implicit pada Pub-Sub

Crash worker atau restart aggregator **tidak menyebabkan duplikasi data** karena deduplikasi dijamin di level storage.

---

## 5. Pengujian Unit & Integrasi (20 Skenario)

Sistem diuji menggunakan **pytest** dengan total **20 file pengujian**, mencakup hampir seluruh failure mode dan skenario konkurensi.

### 5.1 Ringkasan Cakupan Test

| Test                                       | Fokus Pengujian               |
| ------------------------------------------ | ----------------------------- |
| `test_01_schema_validation.py`             | Validasi skema event          |
| `test_02_dedup_basic.py`                   | Deduplikasi dasar             |
| `test_03_batch_atomic.py`                  | Atomisitas batch              |
| `test_04_stats_consistency.py`             | Konsistensi statistik         |
| `test_05_persistence_restart.py`           | Persistensi pasca restart     |
| `test_06_concurrency_upsert.py`            | **Konkurensi upsert paralel** |
| `test_07_ordering_and_timestamp.py`        | Ordering berbasis waktu       |
| `test_08_invalid_payload.py`               | Penanganan error payload      |
| `test_09_large_payload.py`                 | Payload besar                 |
| `test_10_health_and_observability.py`      | Endpoint health               |
| `test_11_single_event_insert.py`           | Insert tunggal                |
| `test_12_partial_batch_rollback.py`        | Rollback batch                |
| `test_13_same_event_id_different_topic.py` | Event ID lintas topic         |
| `test_14_stats_under_concurrency.py`       | Statistik paralel             |
| `test_15_high_frequency_duplicates.py`     | Duplikasi masif               |
| `test_16_limit_parameter.py`               | Parameter limit               |
| `test_17_topic_filtering.py`               | Filter topic                  |
| `test_18_list_not_empty.py`                | Validasi response             |
| `test_19_stats_keys_exist.py`              | Struktur stats                |
| `test_20_stats_endpoint_stable.py`         | Stabilitas endpoint           |

**Semua pengujian berhasil dijalankan tanpa kegagalan.**

---

## 6. Analisis Performa & Load Testing (k6)

### 6.1 Hasil Uji Beban

Berdasarkan eksekusi terbaru:

| Metrik                 | Nilai  |
| ---------------------- | ------ |
| Total event diterima   | 44.600 |
| Event unik diproses    | 31.274 |
| Event duplikat dibuang | 13.326 |
| Failure rate           | 0.00%  |

### 6.2 Analisis

* Tingkat duplikasi ≈ **29.8%**
* Semua duplikasi berhasil ditangani
* Tidak terjadi lost update
* Melebihi batas minimum **20.000 event** sesuai rubrik

Ini membuktikan sistem mampu bekerja stabil pada kondisi **high concurrency**.

---

## 7. Keterkaitan dengan Teori Bab 1–13

| Bab       | Implementasi                            |
| --------- | --------------------------------------- |
| Bab 1     | Sistem terdistribusi tanpa global clock |
| Bab 2     | Arsitektur Pub-Sub                      |
| Bab 3     | At-least-once delivery                  |
| Bab 4–5   | Identitas event global                  |
| Bab 6     | Failure handling                        |
| Bab 7     | Eventual consistency                    |
| Bab 8     | Transaksi ACID                          |
| Bab 9     | Kontrol konkurensi                      |
| Bab 10–13 | Orkestrasi, keamanan, persistensi       |

---

## 8. Kesimpulan

Proyek ini berhasil mengimplementasikan **Pub-Sub Log Aggregator** yang:

* scalable,
* konsisten,
* tahan kegagalan,
* dan sesuai teori sistem terdistribusi.

Pendekatan **idempotent consumer + transactional upsert** terbukti efektif untuk menangani konkurensi tinggi tanpa koordinasi global.

---

## 9. Referensi (APA 7th)

Coulouris, G., Dollimore, J., Kindberg,  T., & Blair, G. (2012).
*Distributed systems: Concepts and design* (5th ed.). Addison-Wesley.

---

## 10. Cara Menjalankan Sistem

```bash
# Build & run
docker compose up --build -d

# Jalankan seluruh test
pytest tests/ -v

# Load testing
docker compose --profile load up --force-recreate

# Cek statistik
curl http://localhost:8080/stats
```

---
