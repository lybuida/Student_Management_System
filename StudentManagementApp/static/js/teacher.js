// Tính điểm trung bình
function calculateAverage(studentId) {
    const inputs15 = document.querySelectorAll(`#score15_${studentId} input`);
    const inputs1tiet = document.querySelectorAll(`#score1tiet_${studentId} input`);
    const finalInput = document.querySelector(`input[name='score_final_${studentId}']`);
    const avgDisplay = document.getElementById(`avg_${studentId}`);

    let sum = 0, count = 0;

    inputs15.forEach(input => {
        const val = parseFloat(input.value);
        if (!isNaN(val)) {
            sum += val;
            count += 1;
        }
    });

    inputs1tiet.forEach(input => {
        const val = parseFloat(input.value);
        if (!isNaN(val)) {
            sum += val * 2;
            count += 2;
        }
    });

    if (finalInput && finalInput.value !== '') {
        const val = parseFloat(finalInput.value);
        if (!isNaN(val)) {
            sum += val * 3;
            count += 3;
        }
    }

    avgDisplay.textContent = count > 0 ? (sum / count).toFixed(2) : '-';
}

//Thêm ô nhập điểm mới
window.addScoreInput = function (studentId, type) {
    const containerId = type === '15' ? `score15_${studentId}` : `score1tiet_${studentId}`;
    const container = document.getElementById(containerId);
    const max = parseInt(container.dataset.max, 10) || 0;

    if (container.querySelectorAll('input').length >= max) {
        alert(`Không thể nhập quá ${max} điểm ${type === '15' ? '15 phút' : '1 tiết'}`);
        return;
    }

    const input = document.createElement("input");
    input.type = "number";
    input.name = `score_${type}_${studentId}_${Date.now()}`;
    input.className = "form-control score-input";
    input.step = "0.0001";
    input.min = "0";
    input.max = "10";
    input.addEventListener('input', () => calculateAverage(studentId));

    const wrapper = document.createElement("div");
    wrapper.className = "d-flex align-items-center mb-1 gap-2";

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "btn btn-sm btn-outline-danger";
    removeBtn.textContent = "×";
    removeBtn.onclick = () => {
        wrapper.remove();
        calculateAverage(studentId);
    };

    wrapper.appendChild(input);
    wrapper.appendChild(removeBtn);
    container.appendChild(wrapper);
};

// Khi trang load: gắn sự kiện tính lại trung bình cho tất cả input
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.score-input').forEach(input => {
        input.addEventListener('input', (e) => {
            const parts = e.target.name.split('_');
            const studentId = parts[2];
            calculateAverage(studentId);
        });

        // Gọi luôn để hiển thị trung bình ngay từ đầu
        const studentId = input.name.split('_')[2];
        calculateAverage(studentId);
    });
});
