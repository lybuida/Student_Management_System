let quantity_student = 0
let quantity_student_in_class = 0
id_class = 0

let selectedStudent = null
let selectedClassId = null

// ✅ Thêm học sinh
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("add-student-form");
    if (!form) return;

    form.addEventListener("submit", function(e) {
        e.preventDefault();

        const formData = new FormData(form);

        fetch("/staff/ThemHocSinh", {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            const alertSuccess = `<div class="alert alert-success">${data.message}</div>`;
            const alertFail = `<div class="alert alert-danger">${data.error}</div>`;
            const alertContainer = document.querySelector(".card-body .alert");
            if (alertContainer) alertContainer.remove();

            if (data.success) {
                form.insertAdjacentHTML("afterbegin", alertSuccess);
                form.reset();

                const tbody = document.getElementById("list-student");
                const rowCount = tbody.querySelectorAll("tr").length + 1;
                const stu = data.student;
                const row = `
                    <tr>
                        <td>${rowCount}</td>
                        <td>${stu.name}</td>
                        <td>${stu.sex}</td>
                        <td>${stu.DoB}</td>
                        <td>${stu.address || ''}</td>
                        <td>${stu.email}</td>
                        <td>${stu.phonenumber || ''}</td>
                        <td>Khối ${stu.grade}</td>
                        <td><button class="btn btn-danger btn-sm" onclick="deleteStudent(${stu.id})">Xóa</button></td>
                    </tr>
                `;
                tbody.insertAdjacentHTML("beforeend", row);
            } else {
                form.insertAdjacentHTML("afterbegin", alertFail);
            }

            setTimeout(() => {
                const alert = document.querySelector(".card-body .alert");
                if (alert) alert.remove();
            }, 3000);
        });
    });
});


function handleSearch() {
    const searchTerm = document.getElementById('searchInput').value;
    const gradeId = document.getElementById('filterGradeAdd').value;

    fetch("/staff/api/searchStudentAddStu", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ searchstudentAddStu: searchTerm, grade_id: gradeId })
    })
    .then(res => res.json())
    .then(data => renderResults(data));
}


function showAllStudents() {
    const gradeId = document.getElementById('filterGradeAdd').value;
    fetch("/staff/api/searchStudentAddStu", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ searchstudentAddStu: "", grade_id: gradeId })
    })
    .then(res => res.json())
    .then(data => renderResults(data));
}

function renderResults(data) {
    const resultList = document.getElementById('list-student');
    const noResultsDiv = document.getElementById('no-results');

    resultList.innerHTML = '';
    noResultsDiv.style.display = 'none';

    if (data[0].quantity === 0) {
        noResultsDiv.style.display = 'block';
    } else {
        for (let i = 1; i <= data[0].quantity; i++) {
            const student = data[i];
            resultList.innerHTML += `
                <tr data-student-id="${student.id}">
                    <td>${i}</td>
                    <td>${student.name}</td>
                    <td>${student.sex}</td>
                    <td>${student.DoB}</td>
                    <td>${student.address}</td>
                    <td>${student.email}</td>
                    <td>${student.phonenumber}</td>
                    <td>${student.grade}</td>
                    <td><button class="btn btn-sm btn-danger" onclick="deleteStudent(${student.id})">Xóa</button></td>
                </tr>
            `;
        }
    }
}

function deleteStudent(studentId) {
    if (confirm('Bạn chắc chắn muốn xóa học sinh này?')) {
        fetch(`/staff/api/deleteStudent/${studentId}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            if (data.success) showAllStudents();
            else alert(data.error || 'Xóa thất bại');
        })
        .catch(error => alert('Có lỗi xảy ra khi xóa học sinh'));
    }
}

function clearForm() {
    ['fullname', 'sex', 'DoB', 'address', 'email', 'phonenumber', 'grade']
        .forEach(id => document.getElementById(id).value = '');
}

function printClass(id) {
    fetch("/staff/api/printClass", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ id_class: id })
    })
    .then(res => res.json())
    .then(data => {
        id_class = data[0].id
        let a = document.getElementById('no_student')
        let b = document.getElementById('print_class')
        if(data[0].quantity == 0) {
            a.style.display = "inline"
            a.innerHTML = `<div class="alert alert-info text-center">Lớp không có học sinh</div>`
            b.style.display = "none"
        } else {
            document.getElementById('name_class').innerText = `Lớp: ${data[0].class}`
            document.getElementById('quantity').innerText = `Sĩ số: ${data[0].quantity}`
            a.style.display = "none"
            b.style.display = "inline"
            const table = document.getElementById('table_print_class')
            for(let i = 1; i <= quantity_student_in_class; i++) table.deleteRow(1)
            quantity_student_in_class = data[0].quantity
            for(let i = 1; i <= data[0].quantity; i++) {
                let row = table.insertRow()
                row.insertCell().innerText = i
                row.insertCell().innerText = data[i].name
                row.insertCell().innerText = data[i].sex
                row.insertCell().innerText = data[i].DoB
                row.insertCell().innerText = data[i].address
            }

        }
        const button = document.querySelector(`#btn-class-${id}`)
        if(button) {
            button.setAttribute('data-student-count', data[0].quantity)
            button.textContent = `${data[0].class} (${data[0].quantity})`
        }
    });
}

function handleClassButton(classId, buttonElement) {
    document.querySelectorAll('.class-button').forEach(btn => btn.classList.remove('active'))
    buttonElement.classList.add('active')
    printClass(classId)
}

document.addEventListener('DOMContentLoaded', () => {
    const firstClassButton = document.querySelector('.class-button')
    if(firstClassButton) handleClassButton(parseInt(firstClassButton.id.replace('btn-class-', '')), firstClassButton)
})

function loadClassesByGrade(gradeId) {
    const classSelect = document.getElementById('filterClass');
    classSelect.innerHTML = '<option value="">Chọn lớp</option>';
    if (!gradeId) return;
    fetch(`/staff/api/getClassesByGrade/${gradeId}`)
        .then(res => res.json())
        .then(classes => {
            classes.forEach(c => {
                const option = document.createElement('option');
                option.value = c.id_class;
                option.textContent = c.name_class;
                classSelect.appendChild(option);
            });
        });
}

function searchStudent() {
    const name = document.getElementById('searchstudent').value;
    const classId = document.getElementById('filterClass').value;
    fetch("/staff/api/searchStudent", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ searchstudent: name, class_id: classId })
    })
    .then(res => res.json())
    .then(data => {
        const result = document.getElementById("result_searchstudent");
        const noResult = document.getElementById("no_result_searchstudent");
        result.innerHTML = '';
        noResult.innerHTML = '';
        if (data[0].quantity === 0) {
            noResult.innerHTML = '<div class="alert alert-info">Không tìm thấy học sinh</div>';
        } else {
            for (let i = 1; i <= data[0].quantity; i++) {
                const s = data[i];
                const row = `
                    <tr>
                        <td>${s.id}</td>
                        <td>${s.name}</td>
                        <td>${s.class}</td>
                        <td><button class="btn btn-sm btn-primary" onclick="selectStudent(${s.id}, '${s.name}', '${s.class}')">Chọn</button></td>
                    </tr>`;
                result.innerHTML += row;
            }
        }
    });
}

function selectStudent(id, name, className) {
    selectedStudent = { id, name, class: className };
    document.getElementById('studentName').innerText = `${name} (${className})`;
    document.getElementById('btnChangeClass').disabled = false;
}

function selectNewClass(classId, element) {
    if (element.classList.contains('disabled')) return;
    document.querySelectorAll('.class-option').forEach(btn => btn.classList.remove('active'));
    element.classList.add('active');
    selectedClassId = classId;
}

function changeClass() {
    if (!selectedStudent || !selectedClassId) {
        alert("Vui lòng chọn học sinh và lớp mới!");
        return;
    }

    fetch('/staff/change_class', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            student_id: selectedStudent.id,
            new_class_id: selectedClassId
        })
    })
    .then(res => res.json())
    .then(data => {
        const resultDiv = document.getElementById('changeClassResult');
        if (data.success) {
            // Cập nhật số lượng lớp cũ
            if (data.old_class.id) {
                const oldClassBtn = document.querySelector(`.class-option[data-class-id="${data.old_class.id}"]`);
                if (oldClassBtn) {
                    oldClassBtn.textContent = `${data.old_class.name} (${data.old_class.current_student}/${data.max_per_class})`;
                    if (data.old_class.current_student >= data.max_per_class) {
                        oldClassBtn.classList.add('disabled');
                    } else {
                        oldClassBtn.classList.remove('disabled');
                    }
                }
            }

            // Cập nhật số lượng lớp mới
            const newClassBtn = document.querySelector(`.class-option[data-class-id="${data.new_class.id}"]`);
            if (newClassBtn) {
                newClassBtn.textContent = `${data.new_class.name} (${data.new_class.current_student}/${data.max_per_class})`;
                if (data.new_class.current_student >= data.max_per_class) {
                    newClassBtn.classList.add('disabled');
                } else {
                    newClassBtn.classList.remove('disabled');
                }
            }

            // Reset các phần khác
            resultDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
            document.getElementById('studentName').innerText = "Chưa chọn học sinh";
            document.getElementById('btnChangeClass').disabled = true;
            selectedStudent = null;
            selectedClassId = null;
            document.querySelectorAll('.class-option').forEach(btn => btn.classList.remove('active'));
            searchStudent(); // Tải lại danh sách học sinh
        } else {
            resultDiv.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
        }
    })
    .catch(error => {
        alert("Có lỗi xảy ra khi kết nối đến server");
    });
}

setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.transition = 'opacity 0.3s ease-out';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 3000);


