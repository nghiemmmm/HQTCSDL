from typing import List

from fastapi import HTTPException, status
from sqlalchemy import exc
from sqlalchemy.orm.session import Session

from db.model import DbLop, DbSinhVien
from schemas.schemas import SinhVienDisplay, SinhVienWithLopDisplay, SinhVienBase


def lay_ds_sinh_vien_mot_lop(db: Session, malop: str) -> List[SinhVienWithLopDisplay]:
	ma_lop = (malop or "").strip()
	if not ma_lop:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"message": "Ma lop khong duoc de trong"},
		)

	lop = db.query(DbLop).filter(DbLop.malop == ma_lop).first()
	if not lop:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"message": f"Khong tim thay lop co ma: {ma_lop}"},
		)

	try:
		rows = (
			db.query(DbSinhVien)
			.filter(DbSinhVien.malop == ma_lop)
			.order_by(DbSinhVien.masv.asc())
			.all()
		)

		return [SinhVienWithLopDisplay.model_validate(row) for row in rows]
	except exc.SQLAlchemyError as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail={"message": f"Loi khi lay danh sach sinh vien: {str(e)}"},
		)
def sl_sinhvien_mot_lop(db: Session, malop: str) -> int:
	ma_lop = (malop or "").strip()
	if not ma_lop:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"message": "Ma lop khong duoc de trong"},
		)

	lop = db.query(DbLop).filter(DbLop.malop == ma_lop).first()
	if not lop:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"message": f"Khong tim thay lop co ma: {ma_lop}"},
		)

	try:
		count = db.query(DbSinhVien).filter(DbSinhVien.malop == ma_lop).count()
		return count
	except exc.SQLAlchemyError as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail={"message": f"Loi khi dem so luong sinh vien: {str(e)}"},
		)
def delete_sinhvien_lop(db: Session, masv:str, malop: str) -> None:
	"""
	Xóa sinh viên khỏi lớp (cập nhật malop = NULL)
	"""
	ma_lop = (malop or "").strip()
	ma_sv = (masv or "").strip()
	
	if not ma_lop:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"message": "Ma lop khong duoc de trong"},
		)
	
	if not ma_sv:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"message": "Ma sinh vien khong duoc de trong"},
		)

	try:
		# Kiểm tra lớp có tồn tại không
		lop = db.query(DbLop).filter(DbLop.malop == ma_lop).first()
		if not lop:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail={"message": f"Khong tim thay lop co ma: {ma_lop}"},
			)

		# Kiểm tra sinh viên có tồn tại không
		sinhvien = db.query(DbSinhVien).filter(DbSinhVien.masv == ma_sv).first()
		if not sinhvien:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail={"message": f"Khong tim thay sinh vien co ma: {ma_sv}"},
			)

		# Kiểm tra sinh viên có trong lớp này không
		if sinhvien.malop != ma_lop:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail={"message": f"Sinh vien {ma_sv} khong o trong lop {ma_lop}"},
			)

		# Xóa (cập nhật malop thành NULL)
		sinhvien.malop = None
		db.commit()
	except HTTPException:
		raise
	except exc.SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail={"message": f"Loi khi xoa sinh vien khoi lop: {str(e)}"},
		)
def them_sinhvien_lop(db: Session, sinhvien: SinhVienDisplay, malop: str) -> None:
	"""
	Thêm sinh viên vào lớp (cập nhật malop của sinh viên)
	"""
	ma_lop = (malop or "").strip()
	ma_sv = (sinhvien.masv or "").strip()
	
	if not ma_lop:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"message": "Ma lop khong duoc de trong"},
		)
	
	if not ma_sv:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"message": "Ma sinh vien khong duoc de trong"},
		)

	try:
		# Kiểm tra lớp có tồn tại không
		lop = db.query(DbLop).filter(DbLop.malop == ma_lop).first()
		if not lop:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail={"message": f"Khong tim thay lop co ma: {ma_lop}"},
			)

		# Kiểm tra sinh viên có tồn tại không
		sinhvien_db = db.query(DbSinhVien).filter(DbSinhVien.masv == ma_sv).first()
		if not sinhvien_db:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail={"message": f"Khong tim thay sinh vien co ma: {ma_sv}"},
			)

		# Kiểm tra sinh viên đã trong lớp này chưa
		if sinhvien_db.malop == ma_lop:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail={"message": f"Sinh vien {ma_sv} da co trong lop {ma_lop}"},
			)

		# Thêm sinh viên vào lớp
		sinhvien_db.malop = ma_lop
		db.commit()
	except HTTPException:
		raise
	except exc.SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail={"message": f"Loi khi them sinh vien vao lop: {str(e)}"},
		)
def sua_sinhvien_lop(db: Session, sinhvien: SinhVienDisplay, malop: str) -> None:
	"""
	Sửa/chuyển sinh viên sang lớp khác (cập nhật malop của sinh viên)
	"""
	ma_lop = (malop or "").strip()
	ma_sv = (sinhvien.masv or "").strip()
	
	if not ma_lop:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"message": "Ma lop khong duoc de trong"},
		)
	
	if not ma_sv:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"message": "Ma sinh vien khong duoc de trong"},
		)

	try:
		# Kiểm tra lớp đích có tồn tại không
		lop = db.query(DbLop).filter(DbLop.malop == ma_lop).first()
		if not lop:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail={"message": f"Khong tim thay lop co ma: {ma_lop}"},
			)

		# Kiểm tra sinh viên có tồn tại không
		sinhvien_db = db.query(DbSinhVien).filter(DbSinhVien.masv == ma_sv).first()
		if not sinhvien_db:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail={"message": f"Khong tim thay sinh vien co ma: {ma_sv}"},
			)

		# Kiểm tra nếu sinh viên đã trong lớp này rồi
		if sinhvien_db.malop == ma_lop:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail={"message": f"Sinh vien {ma_sv} da co trong lop {ma_lop}"},
			)

		# Cập nhật sinh viên sang lớp mới
		sinhvien_db.malop = ma_lop
		db.commit()
	except HTTPException:
		raise
	except exc.SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail={"message": f"Loi khi sua sinh vien sang lop khac: {str(e)}"},
		)

def them_sinhvien(db: Session, sinhvien: SinhVienBase) -> SinhVienDisplay:
	"""
	Thêm sinh viên mới vào database
	"""
	ma_sv = (sinhvien.masv or "").strip()
	
	if not ma_sv:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"message": "Ma sinh vien khong duoc de trong"},
		)
	
	try:
		# Kiểm tra mã SV đã tồn tại chưa
		existing_sv = db.query(DbSinhVien).filter(DbSinhVien.masv == ma_sv).first()
		if existing_sv:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail={"message": f"Ma sinh vien {ma_sv} da ton tai"},
			)
		
		# Kiểm tra lớp tồn tại nếu có malop
		if sinhvien.malop:
			lop = db.query(DbLop).filter(DbLop.malop == sinhvien.malop).first()
			if not lop:
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail={"message": f"Khong tim thay lop co ma: {sinhvien.malop}"},
				)
		
		# Tạo sinh viên mới
		new_sv = DbSinhVien(
			masv=ma_sv,
			ho=sinhvien.ho,
			ten=sinhvien.ten,
			ngaysinh=sinhvien.ngaysinh,
			diachi=sinhvien.diachi,
			malop=sinhvien.malop,
			password=sinhvien.password
		)
		db.add(new_sv)
		db.commit()
		db.refresh(new_sv)
		return SinhVienDisplay.model_validate(new_sv)
	except HTTPException:
		raise
	except exc.SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail={"message": f"Loi khi them sinh vien: {str(e)}"},
		)

def sua_sinhvien(db: Session, masv: str, sinhvien: SinhVienBase) -> SinhVienDisplay:
	"""
	Cập nhật thông tin sinh viên
	"""
	ma_sv = (masv or "").strip()
	
	if not ma_sv:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"message": "Ma sinh vien khong duoc de trong"},
		)
	
	try:
		# Kiểm tra sinh viên tồn tại
		existing_sv = db.query(DbSinhVien).filter(DbSinhVien.masv == ma_sv).first()
		if not existing_sv:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail={"message": f"Khong tim thay sinh vien co ma: {ma_sv}"},
			)
		
		# Kiểm tra lớp tồn tại nếu có malop
		if sinhvien.malop:
			lop = db.query(DbLop).filter(DbLop.malop == sinhvien.malop).first()
			if not lop:
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail={"message": f"Khong tim thay lop co ma: {sinhvien.malop}"},
				)
		
		# Cập nhật thông tin
		existing_sv.ho = sinhvien.ho
		existing_sv.ten = sinhvien.ten
		existing_sv.ngaysinh = sinhvien.ngaysinh
		existing_sv.diachi = sinhvien.diachi
		existing_sv.malop = sinhvien.malop
		
		db.commit()
		db.refresh(existing_sv)
		return SinhVienDisplay.model_validate(existing_sv)
	except HTTPException:
		raise
	except exc.SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail={"message": f"Loi khi sua sinh vien: {str(e)}"},
		)

def xoa_sinhvien(db: Session, masv: str) -> None:
	"""
	Xóa sinh viên khỏi database
	"""
	ma_sv = (masv or "").strip()
	
	if not ma_sv:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"message": "Ma sinh vien khong duoc de trong"},
		)
	
	try:
		# Kiểm tra sinh viên tồn tại
		existing_sv = db.query(DbSinhVien).filter(DbSinhVien.masv == ma_sv).first()
		if not existing_sv:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail={"message": f"Khong tim thay sinh vien co ma: {ma_sv}"},
			)
		
		db.delete(existing_sv)
		db.commit()
	except HTTPException:
		raise
	except exc.SQLAlchemyError as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail={"message": f"Loi khi xoa sinh vien: {str(e)}"},
		)