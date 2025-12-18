# Bagian Teori – Sistem Terdistribusi (Pub-Sub Log Aggregator)

**Nama**  : Muhammad Azka Yunastio  
**NIM**   : 11231036  
**Mata Kuliah** : Sistem Terdistribusi dan Paralel A 

## T1 (Bab 1) – Karakteristik Sistem Terdistribusi & Trade-off Pub-Sub Aggregator
Sistem terdistribusi dicirikan oleh **konkurensi**, **tidak adanya global clock**, dan **kegagalan independen** (Coulouris et al., 2012). Pada Pub-Sub aggregator, banyak publisher mengirim event secara paralel, subscriber memproses asinkron, dan kegagalan satu worker tidak menghentikan sistem. Trade-off utama adalah **konsistensi vs ketersediaan** serta **latensi vs reliabilitas**.  
Rancangan memilih **at-least-once delivery** untuk meningkatkan ketersediaan dan toleransi kegagalan, dengan konsekuensi potensi duplikasi. Risiko ini diatasi melalui **idempotent consumer** dan **dedup store** sehingga hasil akhir tetap benar. Loose coupling Pub-Sub memudahkan skalabilitas dibanding client–server, tetapi mengorbankan ordering global. Karena tidak ada global clock, ordering ditangani secara praktis (timestamp + counter). Desain menyeimbangkan **scalability, fault tolerance, dan correctness** melalui mekanisme aplikasi, bukan koordinasi global mahal.

---

## T2 (Bab 2) – Kapan Memilih Publish–Subscribe vs Client–Server
Arsitektur **publish–subscribe** cocok ketika produsen dan konsumen perlu **terlepas secara temporal, spasial, dan sinkronisasi** (Coulouris et al., 2012). Pada aggregator, publisher tidak mengetahui subscriber, dan subscriber dapat berubah dinamis. Ini unggul untuk **fan-out besar**, **event-driven**, dan **workload bursty** (log/event stream).  
Client–server lebih tepat untuk request–reply sinkron dan kontrol ketat. Pub-Sub mempermudah **replay** dan **reprocessing** event melalui storage persisten. Trade-off-nya adalah kompleksitas di konsumen (ordering, dedup, idempotensi), yang ditangani lewat desain transaksi dan kontrol konkurensi di storage.

---

## T3 (Bab 3) – At-Least-Once vs Exactly-Once & Idempotent Consumer
**At-least-once** menjamin pesan terkirim minimal sekali namun bisa duplikat; **exactly-once** mahal dan kompleks di sistem dengan kegagalan parsial (Coulouris et al., 2012).  
Aggregator memilih at-least-once demi **fault tolerance**. Efek exactly-once dicapai **secara semantik** lewat **idempotent consumer**: setiap event punya `event_id` unik; duplikasi menjadi no-op. Implementasi database menggunakan **upsert + unique constraint**, mencegah lost-update/double-insert. Pendekatan ini skalabel dan praktis.

---

## T4 (Bab 4) – Skema Penamaan Topic & Event_ID untuk Dedup
Penamaan harus **unik, stabil, dan collision-resistant** (Coulouris et al., 2012). **Topic** merepresentasikan kategori (mis. `persist`, `audit`), sedangkan `event_id` mengidentifikasi event global.  
Skema `event_id` berbasis **UUID** atau komposit (**source + timestamp + counter**) menekan collision tanpa koordinasi terpusat. Dedup dilakukan via **durable store** dengan **unique constraint**. Topic hierarkis memudahkan routing dan subscription selektif.

---

## T5 (Bab 5) – Ordering Praktis: Timestamp + Monotonic Counter
Tanpa global clock, total order sulit (Coulouris et al., 2012). Aggregator memakai **ordering praktis**: timestamp + **monotonic counter per source**.  
Timestamp memberi urutan kasar lintas node; counter menjamin urutan lokal saat timestamp sama. Ini cukup untuk log/analitik, namun **tidak menjamin total order global**. Dampaknya, subscriber toleran terhadap sedikit reordering lintas source. Trade-off ini menghindari koordinasi mahal (consensus).

---

## T6 (Bab 6) – Failure Modes & Mitigasi
Failure umum: **message loss/duplication, worker crash, network partition** (Coulouris et al., 2012). Mitigasi: **retry + backoff**, **durable message store**, **crash recovery**.  
Jika worker crash sebelum commit, event dikirim ulang; **dedup + idempotent write** mencegah efek ganda. Backoff mencegah thundering herd saat pulih. Durable storage memastikan event tidak hilang.

---

## T7 (Bab 7) – Eventual Consistency pada Aggregator
Aggregator bersifat **eventually consistent**: semua subscriber konsisten setelah propagasi selesai (Coulouris et al., 2012).  
Idempotensi dan dedup menjamin **state akhir identik** meski ada delay/reordering. Cocok untuk log/monitoring yang tidak membutuhkan strong consistency, menukar konsistensi kuat dengan **availability dan scalability**.

---

## T8 (Bab 8) – Desain Transaksi: ACID, Isolation & Lost-Update
Transaksi menjamin **ACID** (Coulouris et al., 2012). Aggregator memakai transaksi lokal untuk **menulis event + dedup record** secara atomik.  
Isolation **READ COMMITTED / REPEATABLE READ** cukup mencegah dirty read. **Unique constraint pada event_id** dan **atomic upsert** mencegah lost-update tanpa serializable mahal. Pendekatan ini aman dan sederhana.

---

## T9 (Bab 9) – Kontrol Konkurensi: Locking, Constraint & Idempotent Write
Kontrol konkurensi dapat via locking, OCC, atau constraint (Coulouris et al., 2012). Rancangan memilih **constraint-based control**: **unique constraint + upsert**.  
Tanpa locking eksplisit, sistem lebih scalable. **Idempotent write** memastikan dua worker memproses event sama tidak menimbulkan inkonsistensi—satu sukses, lainnya aman gagal.

---

## T10 (Bab 10–13) – Orkestrasi, Keamanan, Persistensi & Observability
**Docker Compose** untuk orkestrasi lokal; **private network** membatasi akses antar-service (Coulouris et al., 2012).  
**Volume** menjamin persistensi broker/database saat restart. **Observability** melalui logging terpusat dan health check membantu diagnosis kegagalan. Praktik ini mendukung deployment yang reproducible, aman, dan mudah dioperasikan.

---

## Referensi (APA 7th)
Coulouris, G., Dollimore, J., Kindberg, T., & Blair, G. (2012). *Distributed systems: Concepts and design* (5th ed.). Addison-Wesley.
