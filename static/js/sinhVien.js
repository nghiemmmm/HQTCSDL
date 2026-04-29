// Danh sach lop duoc tai tu backend
let dsLop = [];
let dsSV = [];
const API_BASE_URL = "http://127.0.0.1:8000";

let selectedMaLop = "";
let selectedLopTen = "";
let selectedStudentIndex = -1;
let currentAction = "view";

const STUDENT_STORAGE_PREFIX = "hqtc-sv-class-";
const DELETED_STORAGE_PREFIX = "hqtc-sv-deleted-";

const selectedClassInfo = document.getElementById("selectedClassInfo");
const btnClassAdd = document.getElementById("btnClassAdd");
const btnClassDelete = document.getElementById("btnClassDelete");
const btnClassEdit = document.getElementById("btnClassEdit");
const btnClassRestore = document.getElementById("btnClassRestore");
const btnClassSearch = document.getElementById("btnClassSearch");
const btnClassSave = document.getElementById("btnClassSave");
const btnDetailAdd = document.getElementById("btnDetailAdd");
const btnDetailDelete = document.getElementById("btnDetailDelete");
const btnDetailEdit = document.getElementById("btnDetailEdit");
const btnDetailRestore = document.getElementById("btnDetailRestore");
const btnDetailSearch = document.getElementById("btnDetailSearch");
const btnDetailSave = document.getElementById("btnDetailSave");
const txtMaSV = document.getElementById("txtMaSV");
const txtHoTen = document.getElementById("txtHoTen");
const txtNgaySinh = document.getElementById("txtNgaySinh");
const viewMaSV = document.getElementById("viewMaSV");
const viewHoTen = document.getElementById("viewHoTen");
const viewNgaySinh = document.getElementById("viewNgaySinh");
const viewMaLop = document.getElementById("viewMaLop");

// Form và button cho lớp
const formLop = document.getElementById("formLop");
const formSinhVien = document.getElementById("formSinhVien");
const txtMaLop = document.getElementById("txtMaLop");
const txtTenLop = document.getElementById("txtTenLop");
const viewClassMa = document.getElementById("viewClassMa");
const viewClassTen = document.getElementById("viewClassTen");
const btnLopSave = document.getElementById("btnLopSave");
const btnLopCancel = document.getElementById("btnLopCancel");
const btnDetailSaveForm = document.getElementById("btnDetailSaveForm");
const btnDetailCancel = document.getElementById("btnDetailCancel");

let currentFormAction = ""; // "add_lop", "edit_lop", "add_sv", "edit_sv"
let editingMaLop = ""; // Lưu mã lớp cũ khi sửa

function showLopForm() {
    if (formLop) formLop.style.display = "block";
    if (formSinhVien) formSinhVien.style.display = "none";
}

function showSinhVienForm() {
    if (formSinhVien) formSinhVien.style.display = "grid";
    if (formLop) formLop.style.display = "none";
}

function hideAllForms() {
    if (formLop) formLop.style.display = "none";
    if (formSinhVien) formSinhVien.style.display = "none";
}

function clearLopForm() {
    if (txtMaLop) txtMaLop.value = "";
    if (txtTenLop) txtTenLop.value = "";
    if (viewClassMa) viewClassMa.textContent = "Chưa chọn";
    if (viewClassTen) viewClassTen.textContent = "Chưa chọn";
}

function setSelectedClassInfo() {
    if (!selectedClassInfo) {
        return;
    }

    if (!selectedMaLop) {
        selectedClassInfo.textContent = "Chưa chọn lớp";
        return;
    }

    selectedClassInfo.textContent = `Đang thao tác với lớp: ${selectedMaLop}${selectedLopTen ? ` - ${selectedLopTen}` : ""}`;
}

function normalizeDateValue(value) {
    if (!value) {
        return "";
    }

    if (typeof value === "string") {
        return value.slice(0, 10);
    }

    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? "" : parsed.toISOString().slice(0, 10);
}

function normalizeStudent(student, malop) {
    return {
        maSV: ((student?.maSV ?? student?.masv ?? "") + "").trim(),
        hoTen: ((student?.hoTen ?? `${student?.ho ?? ""} ${student?.ten ?? ""}`) + "").trim(),
        ngaySinh: normalizeDateValue(student?.ngaySinh ?? student?.ngaysinh),
        malop: ((student?.malop ?? malop ?? "") + "").trim(),
    };
}

function getClassStorageKey(malop) {
    return `${STUDENT_STORAGE_PREFIX}${malop}`;
}

function getDeletedStorageKey(malop) {
    return `${DELETED_STORAGE_PREFIX}${malop}`;
}

function readStoredList(key) {
    try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

function writeStoredList(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

function getStoredStudents(malop) {
    const rows = readStoredList(getClassStorageKey(malop));
    return Array.isArray(rows) ? rows.map((item) => normalizeStudent(item, malop)) : null;
}

function saveStoredStudents() {
    if (!selectedMaLop) {
        return;
    }

    writeStoredList(getClassStorageKey(selectedMaLop), dsSV);
}

function getDeletedStudents(malop) {
    const rows = readStoredList(getDeletedStorageKey(malop));
    return Array.isArray(rows) ? rows.map((item) => normalizeStudent(item, malop)) : [];
}

function saveDeletedStudents(rows) {
    if (!selectedMaLop) {
        return;
    }

    writeStoredList(getDeletedStorageKey(selectedMaLop), rows);
}

function clearStudentForm() {
    txtMaSV.value = "";
    txtMaSV.disabled = false;
    txtHoTen.value = "";
    txtNgaySinh.value = "";
    renderSelectedStudentInfo(null);
}

function fillStudentForm(student) {
    txtMaSV.value = student?.maSV || "";
    txtHoTen.value = student?.hoTen || "";
    txtNgaySinh.value = normalizeDateValue(student?.ngaySinh);
}

function renderSelectedStudentInfo(student) {
    viewMaSV.textContent = student?.maSV || "Chưa chọn";
    viewHoTen.textContent = student?.hoTen || "Chưa chọn";
    viewNgaySinh.textContent = normalizeDateValue(student?.ngaySinh) || "Chưa chọn";
    viewMaLop.textContent = student?.malop || selectedMaLop || "Chưa chọn";
}

function getFormStudent() {
    return {
        maSV: txtMaSV.value.trim(),
        hoTen: txtHoTen.value.trim(),
        ngaySinh: txtNgaySinh.value.trim(),
        malop: selectedMaLop,
    };
}

function findStudentIndexByKeyword(keyword) {
    const normalized = (keyword || "").trim().toLowerCase();
    if (!normalized) {
        return -1;
    }

    return dsSV.findIndex((student) =>
        student.maSV.toLowerCase().includes(normalized) ||
        student.hoTen.toLowerCase().includes(normalized)
    );
}

function requireSelectedClass() {
    if (!selectedMaLop) {
        alert("Vui lòng chọn một lớp trước khi thao tác sinh viên");
        return false;
    }

    return true;
}

function bindMirrorButton(detailButton, primaryButton) {
    if (!detailButton || !primaryButton) {
        return;
    }

    detailButton.onclick = () => primaryButton.click();
}

function selectStudent(index) {
    selectedStudentIndex = index;
    const student = dsSV[index] || null;
    if (student) {
        showSinhVienForm();
        fillStudentForm(student);
    }
    renderSelectedStudentInfo(student);
    renderGridSV();
}

function selectClass(lop) {
    selectedMaLop = lop.maLop;
    selectedLopTen = lop.tenLop;
    selectedStudentIndex = -1;
    currentAction = "view";
    setSelectedClassInfo();
    renderSelectedStudentInfo(null);
    loadSVFromServer(selectedMaLop);
    renderGridLop();
}

// Render grid lớp
function renderGridLop() {
    const tbody = document.querySelector("#gridLop tbody");
    tbody.innerHTML = "";
    dsLop.forEach(lop => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${lop.maLop}</td><td>${lop.tenLop}</td>`;
        if (lop.maLop === selectedMaLop) {
            tr.classList.add("selected-row");
        }

        tr.onclick = () => selectClass(lop);
        tbody.appendChild(tr);
    });
}

async function loadLopFromServer() {
    try {
        const response = await fetch(`${API_BASE_URL}/lop/lophoc`);
        if (!response.ok) {
            throw new Error("Khong the tai danh sach lop hoc");
        }

        const rows = await response.json();
        dsLop = (rows || []).map((item) => ({
            maLop: ((item.malop ?? item.maLop ?? "") + "").trim(),
            tenLop: ((item.tenlop ?? item.tenLop ?? "") + "").trim(),
        }));

        if (!selectedMaLop && dsLop.length > 0) {
            selectedMaLop = dsLop[0].maLop;
            selectedLopTen = dsLop[0].tenLop;
            setSelectedClassInfo();
        }

        renderGridLop();

        if (selectedMaLop) {
            loadSVFromServer(selectedMaLop);
        }
    } catch (error) {
        alert(error.message || "Tai danh sach lop that bai");
        dsLop = [];
        renderGridLop();
    }
}

// Load danh sach sinh vien cua mot lop tu backend
async function loadSVFromServer(maLop) {
    try {
        const response = await fetch(`${API_BASE_URL}/lop/${encodeURIComponent(maLop)}`);
        if (!response.ok) {
            throw new Error("Khong the tai danh sach sinh vien");
        }

        const storedStudents = getStoredStudents(maLop);
        const rows = await response.json();
        dsSV = (storedStudents || rows || []).map((item) => normalizeStudent(item, maLop));
        selectedStudentIndex = -1;

        renderGridSV();
    } catch (error) {
        alert(error.message || "Tai danh sach sinh vien that bai");
        dsSV = getStoredStudents(maLop) || [];
        renderGridSV();
    }
}

// Render grid sinh viên
function renderGridSV() {
    const tbody = document.querySelector("#gridSV tbody");
    tbody.innerHTML = "";
    dsSV.forEach((sv, index) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${sv.maSV}</td><td>${sv.hoTen}</td><td>${sv.ngaySinh}</td>`;
        if (index === selectedStudentIndex) {
            tr.classList.add("selected-row");
        }

        tr.onclick = () => {
            currentAction = "view_sv";
            selectStudent(index);
        };
        tbody.appendChild(tr);
    });
}

if (btnClassAdd) {
    btnClassAdd.onclick = () => {
        currentFormAction = "add_lop";
        editingMaLop = "";
        clearLopForm();
        showLopForm();
        if (txtMaLop) txtMaLop.focus();
    };
}

if (btnClassEdit) {
    btnClassEdit.onclick = () => {
        if (!selectedMaLop) {
            alert("Vui lòng chọn một lớp để hiệu chỉnh");
            return;
        }

        currentFormAction = "edit_lop";
        editingMaLop = selectedMaLop;
        if (txtMaLop) txtMaLop.value = selectedMaLop;
        if (txtMaLop) txtMaLop.disabled = true;
        if (txtTenLop) txtTenLop.value = selectedLopTen;
        showLopForm();
        if (txtTenLop) txtTenLop.focus();
    };
}

if (btnClassDelete) {
    btnClassDelete.onclick = async () => {
        if (!selectedMaLop) {
            alert("Vui lòng chọn một lớp để xóa");
            return;
        }

        if (!confirm(`Xóa lớp ${selectedMaLop} - ${selectedLopTen}?\n\nChú ý: Lớp phải không có sinh viên mới có thể xóa!`)) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/lop/${encodeURIComponent(selectedMaLop)}`, {
                method: "DELETE",
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail?.message || "Xóa lớp thất bại");
            }

            alert("Xóa lớp thành công!");
            selectedMaLop = "";
            selectedLopTen = "";
            hideAllForms();
            loadLopFromServer();
        } catch (error) {
            alert(error.message || "Lỗi khi xóa lớp");
        }
    };
}

if (btnClassRestore) {
    btnClassRestore.onclick = () => {
        alert("Chức năng phục hồi lớp không khả dụng. Vui lòng thêm lớp mới.");
    };
}

if (btnClassSearch) {
    btnClassSearch.onclick = () => {
        const keyword = prompt("Nhập mã lớp hoặc tên lớp cần tìm:", "");
        if (keyword === null) return;

        const normalized = (keyword || "").trim().toLowerCase();
        if (!normalized) {
            alert("Vui lòng nhập từ khóa tìm kiếm");
            return;
        }

        const foundIndex = dsLop.findIndex(
            (lop) =>
                lop.maLop.toLowerCase().includes(normalized) ||
                lop.tenLop.toLowerCase().includes(normalized)
        );

        if (foundIndex < 0) {
            alert("Không tìm thấy lớp phù hợp");
            return;
        }

        selectClass(dsLop[foundIndex]);
    };
}

// Handler cho nút Lưu lớp
if (btnLopSave) {
    btnLopSave.onclick = async () => {
        const maLop = (txtMaLop?.value || "").trim();
        const tenLop = (txtTenLop?.value || "").trim();

        if (!maLop) {
            alert("Vui lòng nhập mã lớp");
            txtMaLop?.focus();
            return;
        }

        if (!tenLop) {
            alert("Vui lòng nhập tên lớp");
            txtTenLop?.focus();
            return;
        }

        try {
            let response;
            let url = `${API_BASE_URL}/lop/`;
            let method = "POST";
            let body = { malop: maLop, tenlop: tenLop };

            if (currentFormAction === "edit_lop") {
                url = `${API_BASE_URL}/lop/${encodeURIComponent(editingMaLop)}`;
                method = "PUT";
            }

            response = await fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail?.message || "Lưu lớp thất bại");
            }

            const actionText = currentFormAction === "edit_lop" ? "Sửa" : "Thêm";
            alert(`${actionText} lớp thành công!`);
            currentFormAction = "";
            hideAllForms();
            loadLopFromServer();
        } catch (error) {
            alert(error.message || "Lỗi khi lưu lớp");
        }
    };
}

// Handler cho nút Hủy (form lớp)
if (btnLopCancel) {
    btnLopCancel.onclick = () => {
        currentFormAction = "";
        editingMaLop = "";
        clearLopForm();
        if (txtMaLop) txtMaLop.disabled = false;
        hideAllForms();
    };
}

if (btnClassSave) {
    btnClassSave.onclick = () => {
        alert("Chức năng này dùng cho sinh viên. Vui lòng sử dụng nút 'Ghi' ở phần chi tiết sinh viên.");
    };
}

// Không cần bind nữa vì đã có handler riêng cho sinh viên
// bindMirrorButton(btnDetailAdd, btnClassAdd);
// bindMirrorButton(btnDetailDelete, btnClassDelete);
// bindMirrorButton(btnDetailEdit, btnClassEdit);
// bindMirrorButton(btnDetailRestore, btnClassRestore);
// bindMirrorButton(btnDetailSearch, btnClassSearch);
// bindMirrorButton(btnDetailSave, btnClassSave);

// Handler riêng cho sinh viên - Thêm
if (btnDetailAdd) {
    btnDetailAdd.onclick = () => {
        if (!requireSelectedClass()) {
            return;
        }
        currentFormAction = "add_sv";
        selectedStudentIndex = -1;
        clearStudentForm();
        renderSelectedStudentInfo(null);
        showSinhVienForm();
        if (txtMaSV) txtMaSV.focus();
    };
}

// Handler riêng cho sinh viên - Sửa
if (btnDetailEdit) {
    btnDetailEdit.onclick = () => {
        if (!requireSelectedClass()) {
            return;
        }

        if (selectedStudentIndex < 0 || !dsSV[selectedStudentIndex]) {
            alert("Vui lòng chọn một sinh viên để hiệu chỉnh");
            return;
        }

        currentFormAction = "edit_sv";
        const student = dsSV[selectedStudentIndex];
        if (txtMaSV) {
            txtMaSV.value = student.maSV;
            txtMaSV.disabled = true;
        }
        if (txtHoTen) txtHoTen.value = student.hoTen;
        if (txtNgaySinh) txtNgaySinh.value = normalizeDateValue(student.ngaySinh);
        showSinhVienForm();
        if (txtHoTen) txtHoTen.focus();
    };
}

// Handler riêng cho sinh viên - Xóa
if (btnDetailDelete) {
    btnDetailDelete.onclick = async () => {
        if (!requireSelectedClass()) {
            return;
        }

        if (selectedStudentIndex < 0 || !dsSV[selectedStudentIndex]) {
            alert("Vui lòng chọn một sinh viên để xóa");
            return;
        }

        const student = dsSV[selectedStudentIndex];
        if (!confirm(`Xóa sinh viên ${student.maSV} - ${student.hoTen}?`)) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(student.maSV)}`, {
                method: "DELETE",
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail?.message || "Xóa sinh viên thất bại");
            }

            alert("Xóa sinh viên thành công!");
            selectedStudentIndex = -1;
            renderSelectedStudentInfo(null);
            loadSVFromServer(selectedMaLop);
        } catch (error) {
            alert(error.message || "Lỗi khi xóa sinh viên");
        }
    };
}

// Handler riêng cho sinh viên - Phục hồi
if (btnDetailRestore) {
    btnDetailRestore.onclick = () => {
        if (!requireSelectedClass()) {
            return;
        }

        const deletedStudents = getDeletedStudents(selectedMaLop);
        const restored = deletedStudents.pop();

        if (!restored) {
            alert("Không có sinh viên nào để phục hồi");
            return;
        }

        dsSV.push(normalizeStudent(restored, selectedMaLop));
        saveDeletedStudents(deletedStudents);
        saveStoredStudents();
        renderGridSV();
    };
}

// Handler riêng cho sinh viên - Tìm
if (btnDetailSearch) {
    btnDetailSearch.onclick = () => {
        if (!requireSelectedClass()) {
            return;
        }

        const keyword = prompt("Nhập mã SV hoặc họ tên cần tìm:", "");
        if (keyword === null) {
            return;
        }

        const foundIndex = findStudentIndexByKeyword(keyword);
        if (foundIndex < 0) {
            alert("Không tìm thấy sinh viên phù hợp");
            return;
        }

        currentFormAction = "view_sv";
        selectStudent(foundIndex);
    };
}

// Handler cho nút Lưu sinh viên (form)
if (btnDetailSaveForm) {
    btnDetailSaveForm.onclick = async () => {
        if (!requireSelectedClass()) {
            return;
        }

        const student = getFormStudent();
        if (!student.maSV || !student.hoTen || !student.ngaySinh) {
            alert("Vui lòng nhập đầy đủ thông tin");
            return;
        }

        try {
            let response;
            let method = "POST";
            let url = `${API_BASE_URL}/sinhvien/`;
            
            // Tách hoTen thành ho và ten
            const hoTenParts = student.hoTen.split(" ");
            const ten = hoTenParts.pop() || "";
            const ho = hoTenParts.join(" ") || "";
            
            // Chuẩn bị dữ liệu
            let requestBody = {
                masv: student.maSV,
                ho: ho,
                ten: ten,
                ngaysinh: student.ngaySinh,
                malop: selectedMaLop,
                password: "123456"
            };

            if (currentFormAction === "edit_sv") {
                method = "PUT";
                url = `${API_BASE_URL}/sinhvien/${encodeURIComponent(student.maSV)}`;
                requestBody = {
                    masv: student.maSV,
                    ho: ho,
                    ten: ten,
                    ngaysinh: student.ngaySinh,
                    malop: selectedMaLop
                };
            }

            response = await fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail?.message || "Lưu sinh viên thất bại");
            }

            const actionText = currentFormAction === "edit_sv" ? "Sửa" : "Thêm";
            alert(`${actionText} sinh viên thành công!`);
            currentFormAction = "";
            selectedStudentIndex = -1;
            if (txtMaSV) txtMaSV.disabled = false;
            hideAllForms();
            loadSVFromServer(selectedMaLop);
        } catch (error) {
            alert(error.message || "Lỗi khi lưu sinh viên");
        }
    };
}

// Handler cho nút Hủy (form sinh viên)
if (btnDetailCancel) {
    btnDetailCancel.onclick = () => {
        currentFormAction = "";
        selectedStudentIndex = -1;
        if (txtMaSV) {
            txtMaSV.value = "";
            txtMaSV.disabled = false;
        }
        if (txtHoTen) txtHoTen.value = "";
        if (txtNgaySinh) txtNgaySinh.value = "";
        renderSelectedStudentInfo(null);
        hideAllForms();
    };
}

// Khi load
loadLopFromServer();