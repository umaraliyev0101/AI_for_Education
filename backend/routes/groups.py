"""
Group Management Routes
CRUD operations for academic groups
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from backend.database import get_db
from backend.models.group import Group
from backend.models.user import User
from backend.schemas.group import GroupCreate, GroupUpdate, GroupResponse
from backend.dependencies import require_teacher, get_current_user
import os
import glob
from backend.config import settings

router = APIRouter()


def populate_face_image_paths(groups: List[Group], faces_dir: str, db: Session):
    """
    Populate face_image_path for students if not set but images exist
    """
    print(f"Looking for face images in: {faces_dir}")
    print(f"Directory exists: {os.path.exists(faces_dir)}")
    
    if os.path.exists(faces_dir):
        all_files = os.listdir(faces_dir)
        print(f"All files in directory: {all_files}")
    
    for group in groups:
        for student in group.students:
            print(f"Checking student {student.student_id}, current face_image_path: {student.face_image_path}")
            if not student.face_image_path:
                # Look for existing face image
                pattern = os.path.join(faces_dir, f"student_{student.student_id}_*.jpg")
                print(f"Checking pattern: {pattern}")
                matching_files = glob.glob(pattern)
                print(f"Found {len(matching_files)} matching files: {matching_files}")
                if matching_files:
                    # Use the most recent file
                    latest_file = max(matching_files, key=os.path.getctime)
                    student.face_image_path = latest_file
                    print(f"Populated face_image_path for student {student.student_id}: {latest_file}")
                else:
                    print(f"No matching files found for student {student.student_id}")
    
    # Commit the changes to persist them
    try:
        db.commit()
        print("Database commit successful")
    except Exception as e:
        print(f"Database commit failed: {e}")
        db.rollback()


@router.get("/", response_model=List[GroupResponse])
async def list_groups(
    skip: int = 0,
    limit: int = 100,
    year_level: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all groups with pagination and optional filtering by year level

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        year_level: Filter by year level (1-4)
        db: Database session
        current_user: Authenticated user

    Returns:
        List of groups with their students
    """
    query = db.query(Group).options(joinedload(Group.students))

    if year_level is not None:
        if year_level < 1 or year_level > 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Year level must be between 1 and 4"
            )
        query = query.filter(Group.year_level == year_level)

    groups = query.offset(skip).limit(limit).all()
    
    # Populate face_image_path from existing images if not set
    # Get the absolute path relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    faces_dir = os.path.join(project_root, "uploads", "faces")
    populate_face_image_paths(groups, faces_dir, db)
    
    # Debug: Print what we're sending to frontend
    print("=== SENDING GROUPS TO FRONTEND ===")
    for group in groups:
        print(f"Group: {group.name} (ID: {group.id})")
        print(f"Students count: {len(group.students)}")
        for student in group.students:
            print(f"  Student: {student.name} (ID: {student.student_id}), image_path: {student.face_image_path}")
        print("-" * 50)
    
    return groups


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get group by ID

    Args:
        group_id: Group database ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Group information with its students
    """
    group = db.query(Group).options(joinedload(Group.students)).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )

    # Populate face_image_path from existing images if not set
    # Get the absolute path relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    faces_dir = os.path.join(project_root, "uploads", "faces")
    populate_face_image_paths([group], faces_dir, db)

    # Debug: Print what we're sending to frontend
    print(f"=== SENDING GROUP {group_id} TO FRONTEND ===")
    print(f"Group: {group.name} (ID: {group.id})")
    print(f"Students count: {len(group.students)}")
    for student in group.students:
        print(f"  Student: {student.name} (ID: {student.student_id}), image_path: {student.face_image_path}")
    print("-" * 50)

    return group


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Create a new group (Teacher or Admin)

    Args:
        group_data: Group creation data
        db: Database session
        current_user: Authenticated teacher/admin

    Returns:
        Created group information
    """
    # Validate year level
    if group_data.year_level < 1 or group_data.year_level > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year level must be between 1 and 4"
        )

    # Create new group
    new_group = Group(
        name=group_data.name,
        year_level=group_data.year_level
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    # Load the group with students for the response
    created_group = db.query(Group).options(joinedload(Group.students)).filter(Group.id == new_group.id).first()

    return created_group


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Update group information (Teacher or Admin)

    Args:
        group_id: Group database ID
        group_data: Updated group data
        db: Database session
        current_user: Authenticated teacher/admin

    Returns:
        Updated group information
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )

    # Update fields if provided
    update_data = group_data.model_dump(exclude_unset=True)

    # Validate year level if provided
    if 'year_level' in update_data and (update_data['year_level'] < 1 or update_data['year_level'] > 4):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year level must be between 1 and 4"
        )

    for field, value in update_data.items():
        setattr(group, field, value)

    db.commit()
    db.refresh(group)

    # Load the updated group with students for the response
    updated_group = db.query(Group).options(joinedload(Group.students)).filter(Group.id == group.id).first()

    return updated_group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Delete a group (Teacher or Admin)

    Args:
        group_id: Group database ID
        db: Database session
        current_user: Authenticated teacher/admin

    Returns:
        No content
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )

    # Check if group has students
    if group.students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete group that has students assigned to it"
        )

    db.delete(group)
    db.commit()

    return None
