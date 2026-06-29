
function formatDateToDMY(dateString) {
    if (!dateString) return "";
    const parts = dateString.split("-");
    if (parts.length === 3) {
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
    }
    return dateString;
}

// Danh sach lop duoc tai tu backend

let dsLop = [];

let dsSV = [];

const API_BASE_URL = "http://127.0.0.1:8000";

const pageWrap = document.querySelector(".page-wrap");

const pageMode = pageWrap?.dataset.pageMode || "class";
function getErrorMessage(payload, fallback) {
    const detail = payload?.detail;
    const message = detail?.message || detail?.detail || payload?.message || detail;
    return typeof message === "string" && message.trim() ? message : fallback;
}

async function readErrorMessage(response, fallback) {
    let payload = {};
    try {
        payload = await response.json();
    } catch {
        payload = {};
    }
    return getErrorMessage(payload, fallback);
}

let selectedMaLop = "";

let selectedLopTen = "";

let selectedStudentIndex = -1;

let currentAction = "view";

const PAGE_SIZE = 10;
let classCurrentPage = 1;
let studentCurrentPage = 1;



const STUDENT_STORAGE_PREFIX = "hqtc-sv-class-";

const DELETED_STORAGE_PREFIX = "hqtc-sv-deleted-";



const selectedClassInfo = document.getElementById("selectedClassInfo");

const btnClassAdd = document.getElementById("btnClassAdd");

const btnClassDelete = document.getElementById("btnClassDelete");

const btnClassEdit = document.getElementById("btnClassEdit");

const classListActions = document.querySelector(".class-list-actions");

const classFilterInput = document.getElementById("classFilterInput");

const classFilterClear = document.getElementById("classFilterClear");

const classFilterSummary = document.getElementById("classFilterSummary");

const classPagination = document.getElementById("classPagination");
const studentPagination = document.getElementById("studentPagination");

const classListCard = document.getElementById("classListCard");

const classSelectionPrompt = document.getElementById("classSelectionPrompt");

const studentListCard = document.getElementById("studentListCard");

const studentClassInfo = document.getElementById("studentClassInfo");

const btnBackToClasses = document.getElementById("btnBackToClasses");

const btnDetailAdd = document.getElementById("btnDetailAdd");

const btnDetailDelete = document.getElementById("btnDetailDelete");

const btnDetailEdit = document.getElementById("btnDetailEdit");

const txtMaSV = document.getElementById("txtMaSV");

const txtHoTen = document.getElementById("txtHoTen");

const txtNgaySinh = document.getElementById("txtNgaySinh");

const studentDetailPanel = document.getElementById("studentDetailPanel");

const viewMaSV = document.getElementById("viewMaSV");

const viewHoTen = document.getElementById("viewHoTen");

const viewNgaySinh = document.getElementById("viewNgaySinh");

const viewMaLop = document.getElementById("viewMaLop");



// Form và button cho lớp

const formLop = document.getElementById("formLop");

const formSinhVien = document.getElementById("formSinhVien");

const txtMaLop = document.getElementById("txtMaLop");

const txtTenLop = document.getElementById("txtTenLop");

const classDetailPanel = document.getElementById("classDetailPanel");

const viewClassMa = document.getElementById("viewClassMa");

const viewClassTen = document.getElementById("viewClassTen");

const btnLopSave = document.getElementById("btnLopSave");

const btnLopCancel = document.getElementById("btnLopCancel");

const btnDetailSaveForm = document.getElementById("btnDetailSaveForm");

const btnDetailCancel = document.getElementById("btnDetailCancel");



let currentFormAction = ""; // "add_lop", "edit_lop", "add_sv", "edit_sv"

let editingMaLop = ""; // Lưu mã lớp cũ khi sửa



function showLopForm(showClassDetail = false) {

    if (formLop) formLop.style.display = "block";

    if (formSinhVien) formSinhVien.style.display = "none";

    if (classDetailPanel) {

        classDetailPanel.style.display = showClassDetail ? "block" : "none";

    }

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
    if (txtMaLop) {
        txtMaLop.value = "";
        txtMaLop.disabled = false;
    }
    if (txtTenLop) {
        txtTenLop.value = "";
        txtTenLop.disabled = false;
        txtTenLop.style.backgroundColor = "";
    }
    const errorLop = document.getElementById("errorLop");
    if (errorLop) errorLop.innerText = "";
    if (btnLopSave) btnLopSave.disabled = false;

    if (viewClassMa) viewClassMa.textContent = "Chua chon";
    if (viewClassTen) viewClassTen.textContent = "Chua chon";
    if (classDetailPanel) classDetailPanel.style.display = "none";
}


function updateClassSelectionPrompt() {

    if (!classSelectionPrompt) return;

    classSelectionPrompt.style.display = pageMode === "student" && !selectedMaLop ? "block" : "none";

}

function updateClassActionState() {

    const canActOnClass = pageMode === "class" && Boolean(selectedMaLop) && !currentFormAction;

    if (classListActions) classListActions.style.display = canActOnClass ? "flex" : "none";

    if (btnClassDelete) btnClassDelete.disabled = !canActOnClass;

    if (btnClassEdit) btnClassEdit.disabled = !canActOnClass;

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
    if (txtMaSV) {
        txtMaSV.value = "";
        txtMaSV.disabled = false;
    }
    if (txtHoTen) {
        txtHoTen.value = "";
        txtHoTen.disabled = false;
        txtHoTen.style.backgroundColor = "";
    }
    if (txtNgaySinh) {
        txtNgaySinh.value = "";
        txtNgaySinh.disabled = false;
        txtNgaySinh.style.backgroundColor = "";
    }
    const errorSV = document.getElementById("errorSV");
    if (errorSV) errorSV.innerText = "";
    if (btnDetailSaveForm) btnDetailSaveForm.disabled = false;

    renderSelectedStudentInfo(null);
}



function fillStudentForm(student) {

    if (txtMaSV) txtMaSV.value = student?.maSV || "";

    if (txtHoTen) txtHoTen.value = student?.hoTen || "";

    if (txtNgaySinh) txtNgaySinh.value = normalizeDateValue(student?.ngaySinh);

}



function renderSelectedStudentInfo(student) {

    if (!viewMaSV || !viewHoTen || !viewNgaySinh || !viewMaLop) {

        return;

    }

    if (studentDetailPanel) studentDetailPanel.style.display = student ? "block" : "none";

    viewMaSV.textContent = student?.maSV || "Chua chon";

    viewHoTen.textContent = student?.hoTen || "Chua chon";

    viewNgaySinh.textContent = formatDateToDMY(normalizeDateValue(student?.ngaySinh)) || "Chua chon";

    viewMaLop.textContent = student?.malop || selectedMaLop || "Chua chon";

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

    updateClassSelectionPrompt();

    if (pageMode === "class") {

        currentFormAction = "";

        updateClassActionState();

        editingMaLop = "";

        hideAllForms();

    }

    updateClassActionState();

    renderSelectedStudentInfo(null);

    if (studentClassInfo) {

        studentClassInfo.textContent = `Lop dang chon: ${selectedMaLop}${selectedLopTen ? ` - ${selectedLopTen}` : ""}`;

    }

    if (pageMode === "student") {

        if (classListCard) classListCard.style.display = "none";

        if (studentListCard) studentListCard.style.display = "block";

        hideAllForms();

    }

    loadSVFromServer(selectedMaLop);

    renderGridLop();

}



function getClassFilterKeyword() {

    return (classFilterInput?.value || "").trim().toLowerCase();

}



function getFilteredClasses() {

    const keyword = getClassFilterKeyword();

    if (!keyword) {

        return dsLop;

    }



    return dsLop.filter((lop) =>

        lop.maLop.toLowerCase().includes(keyword) ||

        lop.tenLop.toLowerCase().includes(keyword)

    );

}



function renderPager(container, totalRows, currentPage, totalPages, onPageChangeName) {

    if (!container) return;

    if (totalRows <= PAGE_SIZE) {

        container.innerHTML = totalRows ? `Hien thi ${totalRows}/${totalRows}` : "Khong co du lieu";

        return;

    }

    const from = (currentPage - 1) * PAGE_SIZE + 1;

    const to = Math.min(currentPage * PAGE_SIZE, totalRows);

    let buttons = "";

    for (let page = 1; page <= totalPages; page++) {

        buttons += `<button type="button" class="${page === currentPage ? "is-active" : ""}" onclick="${onPageChangeName}(${page})">${page}</button>`;

    }

    container.innerHTML = `
        <span>Hien thi ${from}-${to} trong ${totalRows}</span>
        <button type="button" ${currentPage <= 1 ? "disabled" : ""} onclick="${onPageChangeName}(${currentPage - 1})">Truoc</button>
        ${buttons}
        <button type="button" ${currentPage >= totalPages ? "disabled" : ""} onclick="${onPageChangeName}(${currentPage + 1})">Sau</button>
    `;

}

window.goToClassPage = function(page) {

    classCurrentPage = page;

    renderGridLop();

};

window.goToStudentPage = function(page) {

    studentCurrentPage = page;

    renderGridSV();

};

// Render grid lop

function renderGridLop() {

    const tbody = document.querySelector("#gridLop tbody");

    tbody.innerHTML = "";

    const rows = getFilteredClasses();

    const keyword = getClassFilterKeyword();



    if (classFilterSummary) {

        classFilterSummary.textContent = keyword

            ? `Tim thay ${rows.length}/${dsLop.length} lop`

            : `${dsLop.length} lop`;

    }



    const totalRows = rows.length;

    const totalPages = Math.ceil(totalRows / PAGE_SIZE) || 1;

    if (classCurrentPage > totalPages) classCurrentPage = totalPages;

    if (classCurrentPage < 1) classCurrentPage = 1;

    const pageRows = rows.slice((classCurrentPage - 1) * PAGE_SIZE, classCurrentPage * PAGE_SIZE);



    if (pageRows.length === 0) {

        const tr = document.createElement("tr");

        tr.innerHTML = `<td colspan="2" class="empty-cell">Khong co lop phu hop</td>`;

        tbody.appendChild(tr);

        renderPager(classPagination, totalRows, classCurrentPage, totalPages, "goToClassPage");

        return;

    }



    pageRows.forEach(lop => {

        const tr = document.createElement("tr");

        tr.innerHTML = `<td>${lop.maLop}</td><td>${lop.tenLop}</td>`;

        if (lop.maLop === selectedMaLop) {

            tr.classList.add("selected-row");

        }



        tr.onclick = () => selectClass(lop);

        tbody.appendChild(tr);

    });

    renderPager(classPagination, totalRows, classCurrentPage, totalPages, "goToClassPage");

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
        if (selectedMaLop && !dsLop.some((lop) => lop.maLop === selectedMaLop)) {

            selectedMaLop = "";

            selectedLopTen = "";

        }

        setSelectedClassInfo();

        updateClassActionState();

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

        // const response = await fetch(`${API_BASE_URL}/sinhvien/lop/${encodeURIComponent(maLop)}`);

        if (!response.ok) {

            throw new Error("Khong the tai danh sach sinh vien");

        }



        const storedStudents = getStoredStudents(maLop);

        const rows = await response.json();

        dsSV = (storedStudents || rows || []).map((item) => normalizeStudent(item, maLop));

        selectedStudentIndex = -1;

        studentCurrentPage = 1;



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

    if (!tbody) {

        return;

    }

    tbody.innerHTML = "";

    const totalRows = dsSV.length;

    const totalPages = Math.ceil(totalRows / PAGE_SIZE) || 1;

    if (studentCurrentPage > totalPages) studentCurrentPage = totalPages;

    if (studentCurrentPage < 1) studentCurrentPage = 1;

    const pageRows = dsSV

        .map((sv, index) => ({ sv, index }))

        .slice((studentCurrentPage - 1) * PAGE_SIZE, studentCurrentPage * PAGE_SIZE);

    if (pageRows.length === 0) {

        const tr = document.createElement("tr");

        tr.innerHTML = `<td colspan="3" class="empty-cell">Khong co sinh vien</td>`;

        tbody.appendChild(tr);

        renderPager(studentPagination, totalRows, studentCurrentPage, totalPages, "goToStudentPage");

        return;

    }

    pageRows.forEach(({ sv, index }) => {

        const tr = document.createElement("tr");

        tr.innerHTML = `<td>${sv.maSV}</td><td>${sv.hoTen}</td><td>${formatDateToDMY(sv.ngaySinh)}</td>`;

        if (index === selectedStudentIndex) {

            tr.classList.add("selected-row");

        }



        tr.onclick = () => {

            currentAction = "view_sv";

            selectStudent(index);

        };

        tbody.appendChild(tr);

    });

    renderPager(studentPagination, totalRows, studentCurrentPage, totalPages, "goToStudentPage");

}

if (btnClassAdd) {

    btnClassAdd.onclick = () => {

        currentFormAction = "add_lop";

        editingMaLop = "";

        clearLopForm();

        updateClassActionState();

        showLopForm(false);

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

        if (txtTenLop) { txtTenLop.value = selectedLopTen; txtTenLop.disabled = false; txtTenLop.style.backgroundColor = ""; }
        const errorLop = document.getElementById("errorLop");
        if (errorLop) errorLop.innerText = "";
        if (btnLopSave) btnLopSave.disabled = false;

        if (viewClassMa) viewClassMa.textContent = selectedMaLop;

        if (viewClassTen) viewClassTen.textContent = selectedLopTen || "Chua chon";

        updateClassActionState();

        showLopForm(true);

        if (txtTenLop) txtTenLop.focus();

    };

}



if (btnClassDelete) {

    btnClassDelete.onclick = async () => {

        if (!selectedMaLop) {

            alert("Vui long chon mot lop de xoa");

            return;

        }



        if (dsSV.length > 0) {

            alert("Khong the xoa lop vi da co sinh vien");

            return;

        }

        const className = selectedLopTen ? `${selectedMaLop} - ${selectedLopTen}` : selectedMaLop;

        if (!confirm(`Ban co muon xoa lop ${className}?`)) {

            return;

        }

        try {

            const response = await fetch(`${API_BASE_URL}/lop/${encodeURIComponent(selectedMaLop)}`, {

                method: "DELETE",

            });



            if (!response.ok) {

                const message = await readErrorMessage(response, "Xoa lop that bai");

                if ((message + "").toLowerCase().includes("sinh")) {

                    throw new Error("Khong the xoa lop vi da co sinh vien");

                }

                throw new Error(message);

            }



            alert("Xoa lop thanh cong!");

            selectedMaLop = "";

            selectedLopTen = "";

            setSelectedClassInfo();

            updateClassActionState();

            hideAllForms();

            loadLopFromServer();

        } catch (error) {

            alert(error.message || "Loi khi xoa lop");

        }

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

                const message = await readErrorMessage(response, "Luu lop that bai");

                throw new Error(message);

            }



            const actionText = currentFormAction === "edit_lop" ? "Sửa" : "Thêm";

            alert(`${actionText} lớp thành công!`);

            currentFormAction = "";

            updateClassActionState();

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

        updateClassActionState();

        editingMaLop = "";

        clearLopForm();

        if (txtMaLop) txtMaLop.disabled = false;

        hideAllForms();

    };

}





// Không cần bind nữa vì đã có handler riêng cho sinh viên

// bindMirrorButton(btnDetailAdd, btnClassAdd);

// bindMirrorButton(btnDetailDelete, btnClassDelete);

// bindMirrorButton(btnDetailEdit, btnClassEdit);



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

        if (txtHoTen) { txtHoTen.value = student.hoTen; txtHoTen.disabled = false; txtHoTen.style.backgroundColor = ""; }
        if (txtNgaySinh) { txtNgaySinh.value = normalizeDateValue(student.ngaySinh); txtNgaySinh.disabled = false; txtNgaySinh.style.backgroundColor = ""; }
        const errorSV = document.getElementById("errorSV");
        if (errorSV) errorSV.innerText = "";
        if (btnDetailSaveForm) btnDetailSaveForm.disabled = false;

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

        try {
            // Kiểm tra xem sinh viên có thể xóa hay không
            console.log(`Checking status for student: /sinhvien/${student.maSV}/check-status`);
            const checkResponse = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(student.maSV)}/check-status`);
            console.log("Check response status:", checkResponse.status);
            
            const checkData = await checkResponse.json();
            console.log("Check data:", checkData);

            if (checkData.da_thi || checkData.da_dang_ky) {
                // Nếu sinh viên đã thi hoặc đã đăng ký, không cho xóa
                let errorMsg = "Sinh viên này ";
                if (checkData.da_thi && checkData.da_dang_ky) {
                    errorMsg += "đã thi và đã đăng ký thi";
                } else if (checkData.da_thi) {
                    errorMsg += "đã thi";
                } else {
                    errorMsg += "đã đăng ký thi";
                }
                errorMsg += ". Không thể xóa!";
                console.log(errorMsg);
                alert(errorMsg);
                return;
            }

            // Nếu chưa thi và chưa đăng ký, hỏi xác nhận
            if (!confirm(`Ban co muon xoa sinh vien ${student.maSV} - ${student.hoTen}?`)) {
                return;
            }

            const response = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(student.maSV)}`, {

                method: "DELETE",

            });



            if (!response.ok) {

                const message = await readErrorMessage(response, "Xoa sinh vien that bai");

                throw new Error(message);

            }



            alert("Xoa sinh vien thanh cong!");

            selectedStudentIndex = -1;

            renderSelectedStudentInfo(null);

            loadSVFromServer(selectedMaLop);

        } catch (error) {

            alert(error.message || "Lỗi khi xóa sinh viên");

        }

    };

}



// Handler riêng cho sinh viên - Phục hồi

// Handler riêng cho sinh viên - Tìm

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

        // Strict Validation
        if (student.maSV.length < 3) {
            alert("Mã sinh viên phải có ít nhất 3 ký tự.");
            return;
        }
        
        const nameWords = student.hoTen.trim().split(/\s+/);
        if (nameWords.length < 2) {
            alert("Họ tên phải có ít nhất 2 từ.");
            return;
        }
        for (let word of nameWords) {
            if (word.length < 2) {
                alert("Họ tên không hợp lệ (mỗi từ phải có ít nhất 2 chữ cái).");
                return;
            }
        }
        
        const birthDate = new Date(student.ngaySinh);
        const currentDate = new Date();
        let age = currentDate.getFullYear() - birthDate.getFullYear();
        if (age < 18) {
            alert("Sinh viên phải đủ 18 tuổi (tính theo năm sinh).");
            return;
        }
        if (age > 100) {
            alert("Sinh viên không được lớn hơn 100 tuổi hợp lý chút đi!");
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

                const message = await readErrorMessage(response, "Luu sinh vien that bai");

                throw new Error(message);

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

btnBackToClasses?.addEventListener("click", () => {

    if (studentListCard) studentListCard.style.display = "none";

    if (classListCard) classListCard.style.display = "block";

    selectedStudentIndex = -1;

    updateClassSelectionPrompt();

    renderSelectedStudentInfo(null);

    hideAllForms();

});

classFilterInput?.addEventListener("input", () => {

    classCurrentPage = 1;

    renderGridLop();

});

classFilterClear?.addEventListener("click", () => {

    if (!classFilterInput) {

        return;

    }



    classFilterInput.value = "";

    classCurrentPage = 1;

    renderGridLop();

    classFilterInput.focus();

});



loadLopFromServer();


function checkDuplicateLop() {
    if (currentFormAction === "add_lop") {
        const val = txtMaLop.value.trim();
        const errorLop = document.getElementById("errorLop");
        if (val) {
            const exists = dsLop.some(item => (item.maLop || "").trim().toLowerCase() === val.toLowerCase());
            if (exists) {
                if (errorLop) errorLop.innerText = `Mã lớp ${val} đã tồn tại`;
                if (btnLopSave) btnLopSave.disabled = true;
                if (txtTenLop) {
                    txtTenLop.disabled = true;
                    txtTenLop.style.backgroundColor = "#e5e7eb";
                }
            } else {
                if (errorLop) errorLop.innerText = "";
                if (btnLopSave) btnLopSave.disabled = false;
                if (txtTenLop) {
                    txtTenLop.disabled = false;
                    txtTenLop.style.backgroundColor = "";
                }
            }
        } else {
            if (errorLop) errorLop.innerText = "";
            if (btnLopSave) btnLopSave.disabled = false;
            if (txtTenLop) {
                txtTenLop.disabled = false;
                txtTenLop.style.backgroundColor = "";
            }
        }
    }
}

async function checkDuplicateSV() {
    if (currentFormAction === "add_sv") {
        const val = txtMaSV.value.trim();
        const errorSV = document.getElementById("errorSV");
        if (val) {
            let exists = dsSV.some(item => (item.maSV || "").trim().toLowerCase() === val.toLowerCase());
            
            if (!exists && val.length >= 3) {
                try {
                    const token = localStorage.getItem("token");
                    const res = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(val)}/check-status`, {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    if (res.ok) {
                        exists = true;
                    }
                } catch (e) {
                    console.error("Duplicate check error:", e);
                }
            }

            if (exists) {
                if (errorSV) errorSV.innerText = `Mã sinh viên ${val} đã tồn tại trong hệ thống!`;
                if (btnDetailSaveForm) btnDetailSaveForm.disabled = true;
                if (txtHoTen) {
                    txtHoTen.disabled = true;
                    txtHoTen.style.backgroundColor = "#e5e7eb";
                }
                if (txtNgaySinh) {
                    txtNgaySinh.disabled = true;
                    txtNgaySinh.style.backgroundColor = "#e5e7eb";
                }
            } else {
                if (errorSV) errorSV.innerText = "";
                if (btnDetailSaveForm) btnDetailSaveForm.disabled = false;
                if (txtHoTen) {
                    txtHoTen.disabled = false;
                    txtHoTen.style.backgroundColor = "";
                }
                if (txtNgaySinh) {
                    txtNgaySinh.disabled = false;
                    txtNgaySinh.style.backgroundColor = "";
                }
            }
        } else {
            if (errorSV) errorSV.innerText = "";
            if (btnDetailSaveForm) btnDetailSaveForm.disabled = false;
            if (txtHoTen) {
                txtHoTen.disabled = false;
                txtHoTen.style.backgroundColor = "";
            }
            if (txtNgaySinh) {
                txtNgaySinh.disabled = false;
                txtNgaySinh.style.backgroundColor = "";
            }
        }
    }
}

if (txtMaLop) {
    ['input', 'change', 'keyup'].forEach(evt => txtMaLop.addEventListener(evt, checkDuplicateLop));
}

if (txtMaSV) {
    ['input', 'change', 'keyup'].forEach(evt => txtMaSV.addEventListener(evt, checkDuplicateSV));
}


if (typeof txtMaLop !== 'undefined' && txtMaLop) {
    
    
}
if (typeof txtMaSV !== 'undefined' && txtMaSV) {
    
    
}


if (typeof txtHoTen !== 'undefined' && txtHoTen) {
    
    
}



function formatNameOnBlur(e) {
    let val = e.target.value;
    if (!val) return;
    val = val.replace(/[^\p{L}\s]/gu, '');
    val = val.replace(/\s+/g, ' ').trim();
    val = val.toLowerCase().replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
    e.target.value = val;
}

function formatClassNameOnBlur(e) {
    let val = e.target.value;
    if (!val) return;
    val = val.replace(/\s+/g, ' ').trim();
    e.target.value = val;
}

if (typeof txtMaLop !== 'undefined' && txtMaLop) {
    txtMaLop.addEventListener('blur', formatIdOnBlur);
}
if (typeof txtMaSV !== 'undefined' && txtMaSV) {
    txtMaSV.addEventListener('blur', formatIdOnBlur);
}
if (typeof txtHoTen !== 'undefined' && txtHoTen) {
    txtHoTen.addEventListener('blur', formatNameOnBlur);
}
if (typeof txtTenLop !== 'undefined' && txtTenLop) {
    txtTenLop.addEventListener('blur', formatClassNameOnBlur);
}


function formatIdOnBlur(e) {
    let val = e.target.value;
    if (!val) return;
    val = val.replace(/[^a-zA-Z0-9]/g, '');
    e.target.value = val.toUpperCase();
    
    // Trigger input event manually so that checkDuplicate gets the latest uppercase/sanitized value
    e.target.dispatchEvent(new Event('input'));
}

// Set max attribute for Ngay Sinh to 18 years ago
if (typeof txtNgaySinh !== 'undefined' && txtNgaySinh) {
    const today = new Date();
    const maxYear = today.getFullYear() - 18;
    const minYear = today.getFullYear() - 100;
    txtNgaySinh.max = `${maxYear}-12-31`;
    txtNgaySinh.min = `${minYear}-01-01`;
}
