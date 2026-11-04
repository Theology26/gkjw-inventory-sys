/**
 * Utilitas Ekspor Laporan Excel (CSV dengan BOM UTF-8) & Cetak Berita Acara PDF
 * Standar Tata Kelola GKJW Sukun
 */

export function exportToCSV(filename, rows, headers) {
  if (!rows || !rows.length) {
    alert('Tidak ada data inventaris untuk diekspor.')
    return
  }

  const headerKeys = Object.keys(headers)
  const headerLabels = Object.values(headers)

  // Buat baris header
  const csvRows = [headerLabels.map((h) => `"${h.replace(/"/g, '""')}"`).join(',')]

  // Buat baris data
  for (const row of rows) {
    const values = headerKeys.map((key) => {
      let val = row[key]
      if (val === null || val === undefined) val = ''
      val = String(val).replace(/"/g, '""')
      return `"${val}"`
    })
    csvRows.push(values.join(','))
  }

  const csvContent = '\uFEFF' + csvRows.join('\r\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function printBeritaAcaraStockOpname({ title, pokjaName, items, officerName }) {
  const printWindow = window.open('', '_blank', 'width=900,height=700')
  if (!printWindow) {
    alert('Pop-up terblokir. Izinkan pop-up peramban untuk mencetak Berita Acara.')
    return
  }

  const todayStr = new Intl.DateTimeFormat('id-ID', {
    dateStyle: 'full'
  }).format(new Date())

  const rowsHtml = items.map((item, idx) => `
    <tr>
      <td style="border: 1px solid #141413; padding: 6px; text-align: center; font-family: monospace;">${idx + 1}</td>
      <td style="border: 1px solid #141413; padding: 6px; font-family: monospace; font-weight: bold;">${item.unit_code}</td>
      <td style="border: 1px solid #141413; padding: 6px;">${item.item_name} (${item.brand_model || '-'})</td>
      <td style="border: 1px solid #141413; padding: 6px;">${item.location_name || '-'}</td>
      <td style="border: 1px solid #141413; padding: 6px; text-align: center; font-weight: 600;">${item.condition_status}</td>
    </tr>
  `).join('')

  const docHtml = `
    <!DOCTYPE html>
    <html lang="id">
    <head>
      <meta charset="UTF-8">
      <title>Berita Acara Stock Opname — GKJW Sukun</title>
      <style>
        body { font-family: 'Plus Jakarta Sans', Arial, sans-serif; color: #141413; margin: 40px; font-size: 12px; }
        .header { text-align: center; border-bottom: 2px solid #141413; padding-bottom: 15px; margin-bottom: 20px; }
        .header h1 { margin: 0; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px; }
        .header p { margin: 4px 0 0 0; font-size: 11px; color: #52514E; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th { border: 1.5px solid #141413; background-color: #ECEAE2; padding: 8px; font-size: 11px; text-align: left; }
        .signature-grid { display: flex; justify-content: space-between; margin-top: 50px; page-break-inside: avoid; }
        .signature-box { width: 45%; text-align: center; }
        .signature-line { margin-top: 70px; border-top: 1px solid #141413; padding-top: 5px; font-weight: bold; }
        @media print {
          body { margin: 20mm; }
          button { display: none; }
        }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>GREJA KRISTEN JAWI WETAN (GKJW) JEMAAT SUKUN</h1>
        <p>Sistem Informasi Inventaris & Arsip Dokumen Aset Gereja</p>
        <p style="font-weight: bold; margin-top: 8px;">BERITA ACARA PEMERIKSAAN & STOCK OPNAME FISIK</p>
      </div>

      <p>Pada hari ini, <strong>${todayStr}</strong>, telah dilakukan pemeriksaan fisik aset gereja untuk komisi/lingkup <strong>${pokjaName || 'Semua Komisi'}</strong> dengan rincian daftar unit barang terlampir di bawah ini:</p>

      <table>
        <thead>
          <tr>
            <th style="width: 5%; text-align: center;">No</th>
            <th style="width: 20%;">ID Stiker Fisik</th>
            <th style="width: 40%;">Nama & Merk Barang</th>
            <th style="width: 20%;">Lokasi Ruangan</th>
            <th style="width: 15%; text-align: center;">Kondisi</th>
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
        </tbody>
      </table>

      <div class="signature-grid">
        <div class="signature-box">
          <p>Petugas / Pengurus Komisi:</p>
          <div class="signature-line">${officerName || 'Pengurus POKJA'}</div>
        </div>
        <div class="signature-box">
          <p>Pengawasan Perbendaharaan Jemaat (PBJ):</p>
          <div class="signature-line">Tim Verifikasi Majelis</div>
        </div>
      </div>

      <script>
        window.onload = function() {
          window.print();
        }
      </script>
    </body>
    </html>
  `

  printWindow.document.open()
  printWindow.document.write(docHtml)
  printWindow.document.close()
}

