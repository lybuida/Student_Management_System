let myChart = null;
let resultData = {};

function statisticsScore() {
    const semesterId = document.getElementById('id_semester').value;
    const subjectId = document.getElementById('id_subject').value;
    const yearId = document.getElementById('id_year').value;

    fetch("/api/statisticsScore", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id_semester: semesterId,
            id_subject: subjectId,
            id_year: yearId
        })
    })
    .then(res => res.json())
    .then(data => {
        if (!data || Object.keys(data).length === 0) throw new Error("Không có dữ liệu");

        document.getElementById('result').style.display = 'block';
        document.getElementById('subject').textContent = `Môn học: ${data[0].subject}`;
        document.getElementById('semester').textContent = `Học kỳ: ${data[0].semester}`;
        document.getElementById('schoolyear').textContent = `Năm học: ${data[0].schoolyear}`;

        const tableBody = document.getElementById('table_result');
        tableBody.innerHTML = '';
        resultData = data;

        for (let i = 1; i <= data[0].quantity; i++) {
            const row = tableBody.insertRow();
            row.innerHTML = `
                <td>${i}</td>
                <td>${data[i].class}</td>
                <td>${data[i].quantity_student}</td>
                <td>${data[i].quantity_passed}</td>
                <td>${data[i].rate}%</td>
            `;
        }

        document.getElementById('no-data').style.display = 'none';
        drawChart();
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Có lỗi xảy ra khi tải dữ liệu. Vui lòng thử lại.');
    });
}

function drawChart() {
    const ctx = document.getElementById('chart');
    const chartType = document.getElementById('select_chart').value;

    if (!resultData || Object.keys(resultData).length === 0) {
        document.getElementById('no-data').style.display = 'flex';
        return;
    }

    if (myChart) myChart.destroy();

    const labels = [];
    const values = [];
    const backgroundColors = [];

    for (let i = 1; i <= resultData[0].quantity; i++) {
        labels.push(resultData[i].class);
        values.push(resultData[i].quantity_passed);
        backgroundColors.push(`rgba(${rand()}, ${rand()}, ${rand()}, 0.7)`);
    }

    myChart = new Chart(ctx, {
        type: chartType,
        data: {
            labels,
            datasets: [{
                label: 'Số lượng đạt',
                data: values,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(c => c.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y}`
                    }
                }
            }
        }
    });
}

function exportExcel() {
    const subject = getText('subject', 'Môn học: ');
    const semester = getText('semester', 'Học kỳ: ');
    const year = getText('schoolyear', 'Năm học: ');

    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet('Báo cáo môn học');

    sheet.mergeCells('A1', 'E1');
    sheet.getCell('A1').value = 'BÁO CÁO TỔNG KẾT MÔN HỌC';
    sheet.getCell('A1').alignment = { horizontal: 'center' };
    sheet.getCell('A1').font = { bold: true, size: 16 };

    sheet.getCell('A3').value = `Môn: ${subject}`;
    sheet.getCell('C3').value = `Học kỳ: ${semester}`;
    sheet.getCell('A4').value = `Năm học: ${year}`;

    const headers = ['STT', 'Lớp', 'Sĩ số', 'Số lượng đạt', 'Tỷ lệ'];
    const headerRow = sheet.addRow(headers);
    formatHeaderRow(headerRow);

    const rows = document.getElementById('table_result').rows;
    for (let row of rows) {
        const data = Array.from(row.cells).map(c => c.textContent);
        const r = sheet.addRow(data);
        r.alignment = { horizontal: 'center' };
        addBorder(r);
    }

    sheet.columns.forEach(c => c.width = 15);

    workbook.xlsx.writeBuffer().then(data => {
        const blob = new Blob([data], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });
        saveAs(blob, `bao_cao_tong_ket_mon_${subject.replace(/\s+/g, '_')}.xlsx`);
    });
}

function changeRule() {
    const quantity = parseInt(document.getElementById('quantity').value);
    const minAge = parseInt(document.getElementById('min_age').value);
    const maxAge = parseInt(document.getElementById('max_age').value);
    const result = document.getElementById('result');

    if (minAge >= maxAge) {
        showAlert(result, 'danger', 'Tuổi nhỏ nhất phải nhỏ hơn tuổi lớn nhất');
        return;
    }

    fetch("/api/changeRule", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity, min_age: minAge, max_age: maxAge })
    })
    .then(res => res.json())
    .then(data => {
        const status = data.status === 200 ? 'success' : 'danger';

        // Cập nhật bảng "QUY ĐỊNH HIỆN TẠI" nếu thành công
        if (data.status === 200 || data.status === 300) {
            document.getElementById('current-quantity').textContent = quantity;
            document.getElementById('current-min-age').textContent = minAge;
            document.getElementById('current-max-age').textContent = maxAge;
        }

        if (data.status === 300) {
            if (confirm(data.content)) {
                fetch("/api/reassign_overloaded", { method: 'POST' })
                    .then(r => r.json())
                    .then(res2 => {
                        showAlert(result, 'success', res2.message);
                        setTimeout(() => result.innerHTML = '', 3000);
                    });
            } else {
                showAlert(result, 'info', 'Thao tác bị huỷ bởi người dùng.');
            }
            return;
        }

        showAlert(result, status, data.content);
        if (status === 'success') {
            setTimeout(() => result.innerHTML = '', 3000);
        }
    })
    .catch(error => {
        showAlert(result, 'danger', 'Có lỗi xảy ra khi cập nhật quy định');
        console.error('Error:', error);
    });
}

// === Tiện ích ===
function rand() {
    return Math.floor(Math.random() * 255);
}

function getText(id, prefix) {
    return document.getElementById(id).textContent.replace(prefix, '');
}

function showAlert(el, type, message) {
    el.innerHTML = `
        <div class="alert alert-${type}">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}
        </div>
    `;
}

function formatHeaderRow(row) {
    row.font = { bold: true };
    row.alignment = { horizontal: 'center' };
    row.eachCell(cell => {
        cell.border = borderStyle();
        cell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFD6EAF8' }
        };
    });
}

function addBorder(row) {
    row.eachCell(cell => {
        cell.border = borderStyle();
    });
}

function borderStyle() {
    return {
        top: { style: 'thin' },
        left: { style: 'thin' },
        bottom: { style: 'thin' },
        right: { style: 'thin' }
    };
}
