from unittest.mock import Mock, patch
import pytest
from schemas.schemas import CauHoiCreate
from services import question_service
from services.exceptions import ValidationError

def test_create_question_assigns_teacher_magv():
    db = Mock()
    user = {"ma": "GV_TEST", "role": "GIANGVIEN"}
    request = CauHoiCreate(
        mamh="ATTT",
        trinhdo="A",
        noidung="Nội dung câu hỏi test?",
        a="Đáp án A",
        b="Đáp án B",
        c="Đáp án C",
        d="Đáp án D",
        dap_an="A",
        magv="GV_OTHER"  # Dù gửi mã GV khác, hệ thống phải tự gán GV_TEST
    )

    with patch("services.question_service.db_bode") as mock_db_bode:
        mock_db_bode.create_bode.return_value = Mock()
        question_service.create_question(db, request, user)
        
        # Verify that request.magv was overridden to GV_TEST
        assert request.magv == "GV_TEST"
        mock_db_bode.create_bode.assert_called_once_with(db, request)

def test_create_question_raises_validation_error_on_duplicate_answers():
    db = Mock()
    user = {"ma": "GV_TEST", "role": "GIANGVIEN"}
    request = CauHoiCreate(
        mamh="ATTT",
        trinhdo="B",
        noidung="Nội dung câu hỏi test?",
        a="Đáp án trùng",
        b="Đáp án trùng",  # Trùng đáp án A và B
        c="Đáp án C",
        d="Đáp án D",
        dap_an="A",
        magv="GV_TEST"
    )

    with pytest.raises(ValidationError) as exc_info:
        question_service.create_question(db, request, user)

    assert str(exc_info.value) == "Bốn đáp án A, B, C, D không được trùng nội dung."
