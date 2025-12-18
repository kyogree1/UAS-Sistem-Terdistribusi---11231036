# K6 Load Test – Pub-Sub Log Aggregator

## Tujuan
Menguji performa sistem Pub-Sub Log Aggregator dengan:
- ≥20.000 event
- ±30% duplikasi
- Batch publish
- Concurrent load

## Cara Menjalankan

Pastikan:
- Docker Compose sudah running
- Aggregator aktif di localhost:8080

Jalankan:
```bash
k6 run publish.js
