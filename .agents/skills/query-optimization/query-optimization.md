1 Dùng phép chọn/chiếu trước, phép kết sau
    Rule: Chọn lọc (SELECT + WHERE) trước khi kết (JOIN) để giảm số lượng bản ghi phải xử lý.
2. Khử phép kết (nếu được)
    Rule: Nếu kết quả in ra chỉ 1 cột và dữ liệu không thay đổi, có thể truy vấn trực tiếp trên bảng cung cấp dữ liệu cho cột đó mà không cần JOIN.
3. Tối ưu điều kiện trong WHERE
    Rule: Nếu một điều kiện xuất hiện nhiều lần trong WHERE, sử dụng các phép biến đổi logic để rút gọn.
        Các phép biến đổi cơ bản:
        P1 ^ (P2 v P3) ≡ (P1 ^ P2) v (P1 ^ P3)
        P1 ^ (P1 v P2 v P3) ≡ P1
        P1 v (P1 ^ P2 ^ P3) ≡ P1
4. Tạo INDEX cho các field thường xuyên dùng trong WHERE
    Rule: Các cột được dùng nhiều trong điều kiện WHERE, JOIN hoặc ORDER BY nên được tạo INDEX để tăng tốc truy vấn.