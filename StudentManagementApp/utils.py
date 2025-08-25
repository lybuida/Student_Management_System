def get_school_year_and_semester(id_semester: str):
    """
    Trả về học kỳ (1 hoặc 2) và năm học tương ứng từ id_semester.
    """
    try:
        sem_id = int(id_semester)
        semester = 2 if sem_id % 2 == 0 else 1
        start_year = 2020 + (sem_id - 1) // 2
        schoolyear = f"{start_year}-{start_year + 1}"
        return semester, schoolyear
    except (ValueError, TypeError):
        return None, "Không xác định"
