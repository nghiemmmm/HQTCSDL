from unittest.mock import Mock, patch
from datetime import datetime
from db.model import DbBoDe, DbPhienThi, DbSinhVien, DbBangDiem, DbMonHoc, DbLop
from schemas.schemas import CauHoiUpdate
from db.db_bode import update_bode
from db.db_exam import submit_exam_with_procedure
from services.exam_service import build_review, build_student_scores
from services.exam_registration_service import list_registrations_in_range

def test_update_bode_calls_sp_phuc_hoi_sua_bo_de():
    db = Mock()
    question = DbBoDe(
        cauhoi=12,
        mamh="MH001",
        magv="GV001",
        trinhdo="A",
        dap_an="B",
        noidung="Old Question",
        a="A",
        b="B",
        c="C",
        d="D"
    )
    request = CauHoiUpdate(
        noidung="New Question",
        dap_an="C"
    )
    
    update_bode(db, question, request)
    
    assert db.execute.called
    called_args = db.execute.call_args[0]
    called_params = called_args[1]
    
    assert "SP_Phuc_Hoi_Sua_Bo_De" in str(called_args[0])
    assert called_params["mach"] == 12
    assert called_params["noidung"] == "New Question"
    assert called_params["dapan"] == "C"
    assert called_params["mamh"] == "MH001"
    assert db.commit.called
    assert db.refresh.called


@patch("services.exam_service.db_exam")
def test_build_review_calls_sp_get_ct_baithi_from_phienthi(mock_db_exam):
    db = Mock()
    user = {"ma": "SV001", "role": "SINHVIEN"}
    
    # Configure mock returns
    student = DbSinhVien(masv="SV001", malop="LH001")
    session = DbPhienThi(
        id=99,
        masv="SV001",
        mamh="MH001",
        lan=1,
        malop="LH001",
        trangthai="DA_NOP",
        diem=8.5,
        batdau_luc=datetime(2026, 6, 18, 10, 0, 0),
        nopbai_luc=datetime(2026, 6, 18, 10, 45, 0)
    )
    subject = DbMonHoc(mamh="MH001", tenmh="Mon 1")
    class_info = DbLop(malop="LH001", tenlop="Lop 1")
    score = DbBangDiem(masv="SV001", mamh="MH001", lan=1, diem=8.5)
    
    mock_db_exam.get_student.return_value = student
    mock_db_exam.get_latest_submitted_session.return_value = session
    mock_db_exam.get_subject.return_value = subject
    mock_db_exam.get_class.return_value = class_info
    mock_db_exam.get_score.return_value = score
    
    # Mock SP result
    mock_row = [
        101,          # CAUHOI
        "Cau hoi 1",  # NOIDUNG
        "Ans A",      # A
        "Ans B",      # B
        "Ans C",      # C
        "Ans D",      # D
        "A",          # DAP_AN
        "A"           # DAP_AN_CHON
    ]
    db.execute.return_value.fetchall.return_value = [mock_row]
    
    result = build_review(db, user, 99)
    
    assert db.execute.called
    assert "SP_GET_CT_BAITHI_FROM_PHIENTHI" in str(db.execute.call_args[0][0])
    
    called_params = db.execute.call_args[0][1]
    assert called_params["masv"] == "SV001"
    assert called_params["mamh"] == "MH001"
    assert called_params["lan"] == 1
    
    assert result["has_result"] is True
    assert len(result["question_results"]) == 1
    assert result["question_results"][0]["text"] == "Cau hoi 1"
    assert result["question_results"][0]["status_key"] == "correct"
    assert result["quick_stats"]["correct_count"] == 1


def test_list_registrations_in_range_calls_sp_get_ds_gvdk():
    db = Mock()
    mock_row = [
        "Lop 1",                     # TENLOP
        "Mon 1",                     # TENMH
        "Giao Vien A",               # HOTEN
        40,                          # SOCAUTHI
        datetime(2026, 6, 18),       # NGAYTHI
        "X"                          # DATHI
    ]
    db.execute.return_value.fetchall.return_value = [mock_row]
    
    result = list_registrations_in_range(db, "2026-06-01", "2026-06-30")
    
    assert db.execute.called
    assert "SP_GET_DS_GVDK" in str(db.execute.call_args[0][0])
    assert len(result) == 1
    assert result[0]["tenlop"] == "Lop 1"
    assert result[0]["tenmh"] == "Mon 1"
    assert result[0]["hoten"] == "Giao Vien A"
    assert result[0]["socauthi"] == 40
    assert result[0]["ngaythi"] == "18/06/2026"
    assert result[0]["dathi"] == "X"


@patch("services.exam_service.db_exam")
def test_build_student_scores_calls_sp_get_mh_dathi_sv(mock_db_exam):
    db = Mock()
    user = {"ma": "SV001", "role": "SINHVIEN"}
    
    student = DbSinhVien(masv="SV001", malop="LH001", ho="Nguyen Van", ten="An")
    mock_db_exam.get_student.return_value = student
    
    # Mock SP result for subjects taken
    mock_row = ["MH001", "Mon Hoc 1"]
    mock_db_exam.get_student_subjects_taken.return_value = [mock_row]
    
    # Mock score results
    score1 = DbBangDiem(masv="SV001", mamh="MH001", lan=1, diem=7.5)
    score2 = DbBangDiem(masv="SV001", mamh="MH001", lan=2, diem=8.5)
    mock_db_exam.get_score.side_effect = [score1, score2]
    
    result = build_student_scores(db, user)
    
    assert mock_db_exam.get_student_subjects_taken.called
    mock_db_exam.get_student_subjects_taken.assert_called_with(db, "SV001")
    
    assert result["student_code"] == "SV001"
    assert result["student_name"] == "Nguyen Van An"
    assert len(result["scores"]) == 1
    assert result["scores"][0]["mamh"] == "MH001"
    assert result["scores"][0]["score1"] == "7.50"
    assert result["scores"][0]["score2"] == "8.50"
    assert result["scores"][0]["highest"] == "8.50"
    assert result["scores"][0]["highest_letter"] == "A"
    assert result["scores"][0]["status_label"] == "Đạt"


def test_submit_exam_with_procedure_calls_sp_insert_kq_thi():
    db = Mock()
    submit_exam_with_procedure(
        db,
        session_id=45,
        score_value=8.25,
        answers_json='{"1": "A"}'
    )
    
    assert db.execute.called
    called_args = db.execute.call_args[0]
    called_params = called_args[1]
    
    assert "SP_INSERT_KQ_THI" in str(called_args[0])
    assert called_params["phienthi_id"] == 45
    assert called_params["diem"] == 8.25
    assert called_params["dapan_dachon"] == '{"1": "A"}'
