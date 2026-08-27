# Audit visual v1 → standar redesign v2

## Diagnosis

Prototype v1 berhasil secara teknis, tetapi gagal secara artistik. Komposisinya memakai tiga panel besar yang seragam, empat metric cards, satu node topology sederhana, dan palet cyan/purple/green yang berulang. Hasilnya terbaca seperti template admin dashboard, bukan identitas personal seorang builder teknologi.

Masalah utama bukan kurangnya widget. Masalahnya adalah tidak ada **hero moment**, tidak ada kedalaman ruang, tidak ada konflik visual, tidak ada focal point yang kuat, dan belum ada alur cerita yang membuat pembaca ingin terus menggulir. Semua panel memiliki bobot visual hampir sama, sehingga mata tidak tahu harus melihat apa lebih dahulu.

## Yang harus dihapus atau dikurangi

| Elemen v1 | Keputusan v2 | Alasan |
| --- | --- | --- |
| Empat metric cards seragam | Hapus dari hero; pindahkan telemetry ke layer sekunder | Terlihat generik dan menghabiskan perhatian |
| Node topology berupa empat lingkaran | Ganti menjadi peta ruang dengan orbit, depth, dan relasi bermakna | Topology v1 terlalu seperti diagram presentasi |
| Border panel berulang | Gunakan frame asimetris, crop, overlap, dan negative space | Menghilangkan ritme monoton |
| Semua warna neon sekaligus | Pilih satu accent utama + status color terbatas | Cyan/purple/green berulang terasa template |
| Judul section besar bertingkat | Ganti dengan label sistem kecil dan focal headline | Mengurangi kesan dashboard biasa |
| Copy generik “building tools” | Ganti dengan statement yang spesifik dan berani | Identitas harus terasa personal |

## Standar kualitas visual v2

- **Focal point:** dalam tiga detik pertama, mata harus tertarik ke satu objek utama, bukan ke empat kartu yang sama kuat.
- **Depth:** gunakan foreground, midground, background, glow, parallax-like layering, dan perspektif; bukan hanya rounded rectangles.
- **Asymmetry:** minimal satu komposisi besar yang sengaja tidak simetris namun tetap seimbang.
- **Narrative:** pembaca harus memahami siapa HazaVVIP, sistem apa yang dibangun, dan proyek mana yang menjadi bukti.
- **Material language:** pilih material visual yang konsisten, misalnya holographic glass + scanline + technical blueprint, bukan campuran efek acak.
- **Motion budget:** maksimal tiga gerakan penting; setiap gerakan harus memiliki arti.
- **Data integrity:** data GitHub menjadi isi visual, bukan alasan untuk menampilkan semua widget.
- **Fallback:** setiap aset animated harus punya static frame yang tetap terlihat indah.
- **Mobile composition:** hero harus tetap terbaca pada lebar sempit; versi mobile boleh menjadi crop/stack berbeda, bukan sekadar mengecilkan desktop.

## Arah art direction yang dipilih untuk eksplorasi

Nama kerja: **The HazaVVIP Signal Array**.

Alih-alih menampilkan control room biasa, README akan terlihat seperti sebuah **artefak antarmuka eksperimental**: sebuah signal array yang memetakan jejak engineering ke ruang digital. Hero utama berisi orb/core yang memancarkan tiga jalur sinyal menuju domain `RECON`, `PACKET`, dan `AUTOMATION`. Repository tidak lagi muncul sebagai kartu rata; ia muncul sebagai artefak/node berlapis dengan orbit, index, dan status.

Palet awal: near-black blue `#050816`, electric cyan `#6EE7FF`, ultraviolet `#8B5CF6`, warm white `#F8FAFC`, serta satu amber warning `#F59E0B`. Tekstur: starfield halus, blueprint grid, glass surface transparan, chromatic edge, dan light bloom yang sangat terkontrol.

## Hipotesis layout v2

```text
[TOP EDGE] tiny system metadata / signal coordinates

[HERO] giant signal core + personal identity + three orbital domain labels
       asymmetric crop, depth layers, one scan sweep

[STORY] a short “mission statement” in a terminal/technical annotation style

[ARTIFACTS] three large project artifacts arranged as a constellation,
            not equal cards; each with role, language, and proof link

[TELEMETRY] one compact signal strip: commits / repos / stars / stack mix

[CONTRIBUTION] contribution terrain or waveform as the closing signature

[FOOTER] communication channels and build metadata
```

## Success test

Redesign v2 dianggap berhasil bila screenshot pertama tidak dapat disalahartikan sebagai template stats dashboard biasa; bila pembaca dapat menyebut satu metafora visual setelah melihatnya; bila proyek nyata HazaVVIP menjadi bagian dari cerita; dan bila versi static tetap terlihat premium meskipun seluruh animasi dimatikan.

## Next step

Buat tiga storyboard hero berbeda sebelum menulis ulang seluruh README:

1. **Signal Array:** orb/core dengan tiga orbital domain.
2. **Deep Space Repository Map:** repository sebagai constellation nodes.
3. **Cybernetic Identity Artifact:** identity card besar dengan layered scan data.

Ketiganya harus diuji sebagai komposisi visual, bukan langsung diproduksi sebagai sistem final.
