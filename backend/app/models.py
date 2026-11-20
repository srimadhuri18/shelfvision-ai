import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    location = Column(String(150), default="Main Branch")
    created_at = Column(DateTime, default=datetime.utcnow)

    shelves = relationship("Shelf", back_populates="store", cascade="all, delete-orphan")


class Shelf(Base):
    __tablename__ = "shelves"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id = Column(String(36), ForeignKey("stores.id"), nullable=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    camera_source = Column(String(255), default="0") # webcam index or video path
    rows = Column(Integer, default=2)
    cols = Column(Integer, default=2)
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="shelves")
    sections = relationship("Section", back_populates="shelf", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="shelf", cascade="all, delete-orphan")
    health_logs = relationship("HealthLog", back_populates="shelf", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shelf_id = Column(String(36), ForeignKey("shelves.id"), nullable=False)
    row_index = Column(Integer, nullable=False)
    col_index = Column(Integer, nullable=False)
    label = Column(String(100), nullable=False)
    expected_product_name = Column(String(100), nullable=False)
    expected_category = Column(String(100), nullable=False)
    capacity = Column(Integer, default=10)
    low_stock_threshold = Column(Integer, default=3)
    
    # Normalized bounding box in range [0.0, 1.0]
    roi_x1 = Column(Float, default=0.0)
    roi_y1 = Column(Float, default=0.0)
    roi_x2 = Column(Float, default=1.0)
    roi_y2 = Column(Float, default=1.0)

    shelf = relationship("Shelf", back_populates="sections")
    alerts = relationship("Alert", back_populates="section")


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    yolo_class = Column(String(100), nullable=False)
    price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shelf_id = Column(String(36), ForeignKey("shelves.id"), nullable=False)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=True)
    section_label = Column(String(100), nullable=True)
    alert_type = Column(String(50), nullable=False) # EMPTY, LOW_STOCK, MISPLACED
    severity = Column(String(20), default="WARNING") # CRITICAL, WARNING, INFO
    message = Column(Text, nullable=False)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    shelf = relationship("Shelf", back_populates="alerts")
    section = relationship("Section", back_populates="alerts")


class HealthLog(Base):
    __tablename__ = "health_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shelf_id = Column(String(36), ForeignKey("shelves.id"), nullable=False)
    health_score = Column(Float, nullable=False)
    availability_pct = Column(Float, nullable=False)
    placement_pct = Column(Float, nullable=False)
    stock_pct = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    shelf = relationship("Shelf", back_populates="health_logs")
