import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,              // 50 Virtual Users
  duration: '1m',      // Cukup 30 detik untuk tembus 20k event
  thresholds: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<2000'] // Longgarkan dikit karena batching berat
  }
};
sleep(1)

export default function () {
  // Generate 50 event per request
  const events = Array.from({ length: 50 }, (_, i) => {
    // Logika 30% Duplicate
    const isDupe = Math.random() < 0.3;
    
    let eventId;
    if (isDupe) {
        // ID Duplikat: Ambil dari kolam kecil (misal 1-100) biar sering tabrakan
        eventId = `dupe-key-${Math.floor(Math.random() * 100)}`;
    } else {
        // ID Unik: Kombinasi Waktu + VU ID + Iterasi + Index Loop
        // __VU dan __ITER adalah variabel global k6
        eventId = `uniq-${Date.now()}-vu${__VU}-it${__ITER}-${i}`;
    }

    return {
      topic: "load-test",
      event_id: eventId,
      timestamp: new Date().toISOString(), // Ingat backendmu butuh format ISO
      source: "k6-generator",
      payload: { 
          val: Math.random(), 
          vu: __VU 
      }
    };
  });

  const payload = JSON.stringify({ events: events });

  // PASTIKAN TIDAK ADA SPASI di antara 'aggregator' dan ':8080'
  const res = http.post("http://aggregator:8080/publish", payload, {
    headers: { "Content-Type": "application/json" },
  });

  check(res, { 
      "status 200": (r) => r.status === 200,
      "accepted > 0": (r) => r.json("accepted") > 0
  });

  sleep(0.5); // Sleep 0.5s biar Docker gak meledak
}