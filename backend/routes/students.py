"""
Student Management Routes
CRUD operations for students
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.student import Student
from backend.models.group import Group
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
    
    # Check if group exists
    group = db.query(Group).filter(Group.id == student_data.group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Group with ID {student_data.group_id} not found"
        )
    
    # Create new student
    new_student = Student(
        student_id=student_data.student_id,
        name=student_data.name,
        email=student_data.email,
        phone=student_data.phone,
        group_id=student_data.group_id,
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


@router.post("/{student_id}/enroll-face-multi", response_model=StudentResponse)
async def enroll_student_face_multi(
    student_id: int,
    face_images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Enroll student's face using multiple images for better accuracy (Teacher or Admin)
    
    Args:
        student_id: Student database ID
        face_images: List of face image files (3-5 recommended)
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Updated student information
    """
    from backend.services.face_recognition_service import get_face_recognition_service
    
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    if not face_images or len(face_images) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one face image is required"
        )
    
    # Ensure face images directory exists
    os.makedirs(settings.FACE_IMAGES_DIR, exist_ok=True)
    
    # Save all images
    image_paths = []
    try:
        for i, face_image in enumerate(face_images):
            # Validate file type
            if not face_image.content_type or not face_image.content_type.startswith("image/"):
                continue
            
            image_filename = f"student_{student.student_id}_{i+1}_{face_image.filename}"
            image_path = os.path.join(settings.FACE_IMAGES_DIR, image_filename)
            
            with open(image_path, "wb") as f:
                content = await face_image.read()
                f.write(content)
            
            image_paths.append(image_path)
        
        if not image_paths:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid image files provided"
            )
        
        # Use face recognition service for multi-image enrollment
        face_service = get_face_recognition_service(db)
        success, message = face_service.enroll_student_from_multiple_images(student_id, image_paths)
        
        if not success:
            # Clean up image files if enrollment failed
            for path in image_paths:
                if os.path.exists(path):
                    os.remove(path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Refresh student data
        db.refresh(student)
        return student
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up image files on error
        for path in image_paths:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-image enrollment failed: {str(e)}"
        )


@router.get("/{student_id}/enrollment-status")
async def get_enrollment_status(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check student's face enrollment status
    
    Args:
        student_id: Student database ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Enrollment status information
    """
    from backend.services.face_recognition_service import get_face_recognition_service
    
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    face_service = get_face_recognition_service(db)
    is_valid, message = face_service.validate_face_encoding(student_id)
    
    return {
        "student_id": student.student_id,
        "name": student.name,
        "enrolled": student.face_encoding is not None,
        "face_image_path": student.face_image_path,
        "encoding_valid": is_valid,
        "validation_message": message
    }


@router.delete("/{student_id}/enrollment", status_code=status.HTTP_200_OK)
async def delete_student_enrollment(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Delete student's face enrollment (Teacher or Admin)
    
    Args:
        student_id: Student database ID
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Success message
    """
    from backend.services.face_recognition_service import get_face_recognition_service
    
    face_service = get_face_recognition_service(db)
    success, message = face_service.delete_student_enrollment(student_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"message": message}


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
    from backend.services.face_recognition_service import get_face_recognition_service
    
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    # Delete face enrollment from both databases
    face_service = get_face_recognition_service(db)
    face_service.delete_student_enrollment(student_id)
    
    # Clean up face image file if it still exists
    if hasattr(student, 'face_image_path'):
        face_image_path = student.face_image_path
        if face_image_path is not None and os.path.exists(str(face_image_path)):
            try:
                os.remove(str(face_image_path))
            except Exception:
                pass
    
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
    from backend.services.face_recognition_service import get_face_recognition_service
    
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
    
    # Ensure face images directory exists
    os.makedirs(settings.FACE_IMAGES_DIR, exist_ok=True)
    
    # Save face image
    image_filename = f"student_{student.student_id}_{face_image.filename}"
    image_path = os.path.join(settings.FACE_IMAGES_DIR, image_filename)
    
    try:
        with open(image_path, "wb") as f:
            content = await face_image.read()
            f.write(content)
        
        # Use face recognition service to generate and store encoding
        face_service = get_face_recognition_service(db)
        success, message = face_service.enroll_student_from_image(student_id, image_path)
        
        if not success:
            # Clean up image file if enrollment failed
            if os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Refresh student data
        db.refresh(student)
        return student
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up image file on error
        if os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enrollment failed: {str(e)}"
        )
