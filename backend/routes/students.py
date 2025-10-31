"""
Student Management Routes
CRUD operations for students
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.student import Student
from backend.models.user import User
from backend.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from backend.dependencies import require_admin, require_teacher, get_current_user
from backend.config import settings
import os
import pickle

router = APIRouter()


@router.get("/", response_model=List[StudentResponse])
async def list_students(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all students with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of students
    """
    query = db.query(Student)
    
    if is_active is not None:
        query = query.filter(Student.is_active == is_active)
    
    students = query.offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get student by ID
    
    Args:
        student_id: Student database ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Student information
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    return student


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Create a new student (Teacher or Admin)
    
    Args:
        student_data: Student creation data
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Created student information
    """
    # Check if student_id already exists
    existing_student = db.query(Student).filter(
        Student.student_id == student_data.student_id
    ).first()
    
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with ID {student_data.student_id} already exists"
        )
    
    # Check if email already exists
    if student_data.email:
        existing_email = db.query(Student).filter(
            Student.email == student_data.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with email {student_data.email} already exists"
            )
    
    # Create new student
    new_student = Student(
        student_id=student_data.student_id,
        name=student_data.name,
        email=student_data.email,
        phone=student_data.phone,
        is_active=student_data.is_active
    )
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    return new_student


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Update student information (Teacher or Admin)
    
    Args:
        student_id: Student database ID
        student_data: Updated student data
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Updated student information
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    # Update fields if provided
    update_data = student_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a student (Admin only)
    
    Args:
        student_id: Student database ID
        db: Database session
        current_user: Authenticated admin
        
    Returns:
        No content
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    db.delete(student)
    db.commit()
    
    return None


@router.post("/{student_id}/enroll-face", response_model=StudentResponse)
async def enroll_student_face(
    student_id: int,
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Enroll student's face for recognition (Teacher or Admin)
    
    Args:
        student_id: Student database ID
        face_image: Face image file
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Updated student information
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    # Validate file type
    if not face_image.content_type or not face_image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Save face image
    image_filename = f"student_{student.student_id}_{face_image.filename}"
    image_path = os.path.join(settings.FACE_IMAGES_DIR, image_filename)
    
    with open(image_path, "wb") as f:
        content = await face_image.read()
        f.write(content)
    
    student.face_image_path = image_path
    
    # Note: Face encoding will be generated by face recognition service
    # This is a placeholder - actual encoding will be done by the service
    db.commit()
    db.refresh(student)
    
    return student
