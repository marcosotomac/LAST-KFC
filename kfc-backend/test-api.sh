#!/bin/bash

# Script para probar el backend desplegado de KFC Orders
# Este script crea un tenant, productos de prueba y una orden

API_BASE="https://zkdukyqf99.execute-api.us-east-1.amazonaws.com"

echo "🚀 Probando Backend de KFC Orders"
echo "=================================="
echo ""

# 1. Crear Tenant
echo "📍 Paso 1: Creando tenant..."
TENANT_RESPONSE=$(curl -s -X POST "$API_BASE/tenants" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "KFC Demo Peru",
    "email": "demo@kfc.com.pe",
    "phone": "+51999888777",
    "address": "Av. Larco 123, Miraflores",
    "city": "Lima",
    "country": "PE"
  }')

echo "Response: $TENANT_RESPONSE"
echo ""

# Extraer tenantId (requiere jq)
if command -v jq &> /dev/null; then
  TENANT_ID=$(echo $TENANT_RESPONSE | jq -r '.data.tenantId // .tenantId')
  echo "✅ Tenant creado: $TENANT_ID"
  echo ""
  
  # 2. Crear Productos
  echo "📦 Paso 2: Creando productos de prueba..."
  
  # Producto 1
  curl -s -X POST "$API_BASE/tenants/$TENANT_ID/products" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Bucket Original 8 piezas",
      "description": "8 piezas de pollo frito original con papas familiares",
      "price": 45.90,
      "category": "Buckets",
      "available": true
    }' | jq '.'
  echo ""
  
  # Producto 2
  curl -s -X POST "$API_BASE/tenants/$TENANT_ID/products" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Alitas Picantes x12",
      "description": "12 alitas picantes con salsa BBQ",
      "price": 28.90,
      "category": "Alitas",
      "available": true
    }' | jq '.'
  echo ""
  
  # Producto 3
  curl -s -X POST "$API_BASE/tenants/$TENANT_ID/products" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Combo Personal",
      "description": "1 pieza de pollo + papas + gaseosa",
      "price": 15.90,
      "category": "Combos",
      "available": true
    }' | jq '.'
  echo ""
  
  # 3. Listar Productos
  echo "📋 Paso 3: Listando productos..."
  PRODUCTS_RESPONSE=$(curl -s -X GET "$API_BASE/tenants/$TENANT_ID/products")
  echo "$PRODUCTS_RESPONSE" | jq '.'
  echo ""
  
  # Extraer primer productId
  FIRST_PRODUCT_ID=$(echo "$PRODUCTS_RESPONSE" | jq -r '.data.products[0].productId // .products[0].productId')
  FIRST_PRODUCT_NAME=$(echo "$PRODUCTS_RESPONSE" | jq -r '.data.products[0].name // .products[0].name')
  FIRST_PRODUCT_PRICE=$(echo "$PRODUCTS_RESPONSE" | jq -r '.data.products[0].price // .products[0].price')
  
  echo "✅ Productos creados exitosamente"
  echo ""
  
  # 4. Crear Orden
  if [ ! -z "$FIRST_PRODUCT_ID" ]; then
    echo "🛒 Paso 4: Creando orden de prueba..."
    ORDER_RESPONSE=$(curl -s -X POST "$API_BASE/tenants/$TENANT_ID/orders" \
      -H "Content-Type: application/json" \
      -d "{
        \"items\": [
          {
            \"productId\": \"$FIRST_PRODUCT_ID\",
            \"quantity\": 2,
            \"price\": $FIRST_PRODUCT_PRICE,
            \"name\": \"$FIRST_PRODUCT_NAME\"
          }
        ],
        \"customerName\": \"Juan Pérez\",
        \"customerPhone\": \"+51999888777\",
        \"deliveryAddress\": \"Av. Larco 456, Miraflores\",
        \"notes\": \"Sin picante por favor\"
      }")
    
    echo "$ORDER_RESPONSE" | jq '.'
    echo ""
    
    ORDER_ID=$(echo "$ORDER_RESPONSE" | jq -r '.data.orderId // .orderId')
    
    if [ ! -z "$ORDER_ID" ]; then
      echo "✅ Orden creada: $ORDER_ID"
      echo ""
      
      # 5. Ver detalle de orden
      echo "🔍 Paso 5: Consultando detalle de la orden..."
      curl -s -X GET "$API_BASE/tenants/$TENANT_ID/orders/$ORDER_ID" | jq '.'
      echo ""
    fi
  fi
  
  # Resumen
  echo "=================================="
  echo "✨ Prueba completada exitosamente"
  echo ""
  echo "📝 Actualiza src/config/api.ts con:"
  echo "   const DEFAULT_TENANT_ID = '$TENANT_ID';"
  echo ""
  
else
  echo "⚠️  jq no está instalado. Instálalo con: brew install jq"
  echo "   Response raw: $TENANT_RESPONSE"
fi
