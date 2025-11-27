"""Validadores usando Pydantic"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class OrderStatus(str, Enum):
    """Estados posibles de una orden"""
    PENDING = "pending"
    KITCHEN = "kitchen"
    PACKAGING = "packaging"
    DELIVERY = "delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    """Roles de usuario"""
    ADMIN = "admin"
    KITCHEN = "kitchen"
    CASHIER = "cashier"
    DELIVERY = "delivery"
    CUSTOMER = "customer"


class OrderItem(BaseModel):
    """Item de una orden"""
    productId: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    name: str = Field(..., min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "productId": "prod_123",
                "quantity": 2,
                "price": 15.99,
                "name": "Bucket Original"
            }
        }


class CreateOrderRequest(BaseModel):
    """Request para crear una orden"""
    items: List[OrderItem] = Field(..., min_length=1)
    customerName: str = Field(..., min_length=1, max_length=200)
    customerPhone: Optional[str] = Field(None, max_length=20)
    deliveryAddress: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError("Order must have at least one item")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "productId": "prod_123",
                        "quantity": 2,
                        "price": 15.99,
                        "name": "Bucket Original"
                    }
                ],
                "customerName": "Juan Pérez",
                "customerPhone": "+51999888777",
                "deliveryAddress": "Av. Larco 123, Miraflores",
                "notes": "Sin picante"
            }
        }


class CreateTenantRequest(BaseModel):
    """Request para crear un tenant"""
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=20)
    address: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    country: str = Field(default="PE", max_length=2)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "KFC Miraflores",
                "email": "miraflores@kfc.com.pe",
                "phone": "+51999888777",
                "address": "Av. Larco 123",
                "city": "Lima",
                "country": "PE"
            }
        }


class CreateProductRequest(BaseModel):
    """Request para crear un producto"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    imageUrl: Optional[str] = None
    available: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Bucket Original 8 piezas",
                "description": "8 piezas de pollo frito original con papas familiares",
                "price": 45.90,
                "category": "Buckets",
                "imageUrl": "https://...",
                "available": True
            }
        }


class RegisterUserRequest(BaseModel):
    """Request para registrar un usuario"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    role: UserRole = Field(default=UserRole.CASHIER)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan@kfc.com",
                "password": "secret123",
                "name": "Juan Pérez",
                "role": "cashier"
            }
        }


class LoginRequest(BaseModel):
    """Request para login"""
    email: EmailStr
    password: str = Field(..., min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan@kfc.com",
                "password": "secret123"
            }
        }
