# ecommerce_mcp_server.py
"""
Servidor MCP que expone las funciones de e-commerce a través del Model Context Protocol.
"""

import asyncio
import json
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from difflib import get_close_matches
import logging

# MCP Server Imports
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Load environment variables
load_dotenv()

# -------------------------
# Configuration
# -------------------------

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
TAX_RATE = 0.08  # 8% tax
SHIPPING_THRESHOLD = 100  # Free shipping above this amount
SHIPPING_COST = 10  # Fixed shipping cost
DISCOUNT_CODES = {
    "WELCOME10": 0.10,  # 10% discount
    "SAVE20": 0.20,     # 20% discount
    "VIP30": 0.30       # 30% discount
}

# -------------------------
# Data Models
# -------------------------

@dataclass
class Product:
    """Product model with all relevant information."""
    id: str
    nombre: str
    precio: float
    stock: int
    características: List[str]
    categoria: str = "General"
    descripcion: str = ""
    rating: float = 0.0
    reviews: int = 0

@dataclass
class CartItem:
    """Cart item model."""
    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float = field(init=False)
    
    def __post_init__(self):
        self.subtotal = self.precio_unitario * self.cantidad

@dataclass
class Cart:
    """Shopping cart model."""
    items: List[CartItem] = field(default_factory=list)
    discount_code: Optional[str] = None
    
    def get_subtotal(self) -> float:
        """Calculate cart subtotal."""
        return sum(item.subtotal for item in self.items)
    
    def get_discount_amount(self) -> float:
        """Calculate discount amount."""
        if self.discount_code and self.discount_code in DISCOUNT_CODES:
            return self.get_subtotal() * DISCOUNT_CODES[self.discount_code]
        return 0.0
    
    def get_tax(self) -> float:
        """Calculate tax amount."""
        subtotal_after_discount = self.get_subtotal() - self.get_discount_amount()
        return subtotal_after_discount * TAX_RATE
    
    def get_shipping(self) -> float:
        """Calculate shipping cost."""
        if self.get_subtotal() >= SHIPPING_THRESHOLD:
            return 0.0
        return SHIPPING_COST
    
    def get_total(self) -> float:
        """Calculate total amount."""
        subtotal = self.get_subtotal()
        discount = self.get_discount_amount()
        tax = self.get_tax()
        shipping = self.get_shipping()
        return subtotal - discount + tax + shipping

# -------------------------
# Enhanced Product Catalog
# -------------------------

PRODUCTOS_DB: Dict[str, Product] = {
    "laptop gamer pro": Product(
        id="LPG001",
        nombre="Laptop Gamer Pro",
        precio=1500,
        stock=10,
        características=["RTX 4070", "32GB RAM", "1TB SSD", "144Hz Display"],
        categoria="Computadoras",
        descripcion="Laptop gaming de alta gama para los juegos más exigentes",
        rating=4.8,
        reviews=127
    ),
    "teclado mecanico rgb": Product(
        id="TEC005",
        nombre="Teclado Mecánico RGB",
        precio=120,
        stock=25,
        características=["Switches Cherry MX", "RGB personalizable", "TKL", "USB-C"],
        categoria="Periféricos",
        descripcion="Teclado mecánico premium con iluminación RGB completa",
        rating=4.6,
        reviews=89
    ),
    "monitor 4k hdr": Product(
        id="MON003",
        nombre="Monitor 4K HDR",
        precio=400,
        stock=5,
        características=["27 pulgadas", "144Hz", "HDR10", "G-Sync Compatible"],
        categoria="Monitores",
        descripcion="Monitor gaming 4K con HDR para una experiencia visual inmersiva",
        rating=4.9,
        reviews=203
    ),
    "mouse gaming pro": Product(
        id="MOU002",
        nombre="Mouse Gaming Pro",
        precio=80,
        stock=15,
        características=["16000 DPI", "RGB", "8 botones programables", "Inalámbrico"],
        categoria="Periféricos",
        descripcion="Mouse gaming profesional con sensor de alta precisión",
        rating=4.7,
        reviews=156
    ),
    "auriculares 7.1": Product(
        id="AUR004",
        nombre="Auriculares Gaming 7.1",
        precio=150,
        stock=8,
        características=["Sonido 7.1 Surround", "Micrófono retráctil", "RGB", "Cancelación de ruido"],
        categoria="Audio",
        descripcion="Auriculares gaming con sonido envolvente para máxima inmersión",
        rating=4.5,
        reviews=94
    )
}

# -------------------------
# Shopping Cart State
# -------------------------

carrito = Cart()
historial_busquedas: List[str] = []

# -------------------------
# Helper Functions
# -------------------------

def find_product_fuzzy(nombre: str) -> Optional[Tuple[str, Product]]:
    """Find product using fuzzy matching."""
    nombre_lower = nombre.strip().lower()
    
    # Exact match
    if nombre_lower in PRODUCTOS_DB:
        return nombre_lower, PRODUCTOS_DB[nombre_lower]
    
    # Fuzzy match
    product_names = list(PRODUCTOS_DB.keys())
    matches = get_close_matches(nombre_lower, product_names, n=1, cutoff=0.6)
    
    if matches:
        match = matches[0]
        return match, PRODUCTOS_DB[match]
    
    return None

def format_price(amount: float) -> str:
    """Format price with currency."""
    return f"${amount:,.2f}"

def get_cart_item_by_product(producto_id: str) -> Optional[CartItem]:
    """Get cart item by product ID."""
    for item in carrito.items:
        if item.producto_id == producto_id:
            return item
    return None

def serialize_cart_item(item: CartItem) -> dict:
    """Serialize CartItem to dict."""
    return {
        "producto_id": item.producto_id,
        "nombre": item.nombre,
        "precio_unitario": item.precio_unitario,
        "cantidad": item.cantidad,
        "subtotal": item.subtotal
    }

def serialize_product(product: Product) -> dict:
    """Serialize Product to dict."""
    return {
        "id": product.id,
        "nombre": product.nombre,
        "precio": product.precio,
        "stock": product.stock,
        "características": product.características,
        "categoria": product.categoria,
        "descripcion": product.descripcion,
        "rating": product.rating,
        "reviews": product.reviews
    }

# -------------------------
# MCP Server Setup
# -------------------------

print("Initializing E-commerce MCP Server...")
app = Server("ecommerce-mcp-server")

# -------------------------
# MCP Tool Handlers
# -------------------------

@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """List all available e-commerce tools."""
    print("MCP Server: Received list_tools request.")
    
    tools = [
        mcp_types.Tool(
            name="buscar_producto",
            description="Busca un producto por nombre con búsqueda fuzzy",
            inputSchema={
                "type": "object",
                "properties": {
                    "nombre_producto": {
                        "type": "string",
                        "description": "Nombre del producto a buscar"
                    }
                },
                "required": ["nombre_producto"]
            }
        ),
        mcp_types.Tool(
            name="agregar_al_carrito",
            description="Agrega productos al carrito con validación de stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "producto": {
                        "type": "string",
                        "description": "Nombre del producto"
                    },
                    "cantidad": {
                        "type": "integer",
                        "description": "Cantidad a agregar",
                        "default": 1
                    }
                },
                "required": ["producto"]
            }
        ),
        mcp_types.Tool(
            name="ver_carrito",
            description="Muestra el carrito detallado con cálculos",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        mcp_types.Tool(
            name="aplicar_descuento",
            description="Aplica un código de descuento al carrito",
            inputSchema={
                "type": "object",
                "properties": {
                    "codigo": {
                        "type": "string",
                        "description": "Código de descuento"
                    }
                },
                "required": ["codigo"]
            }
        ),
        mcp_types.Tool(
            name="remover_del_carrito",
            description="Remueve productos del carrito",
            inputSchema={
                "type": "object",
                "properties": {
                    "producto": {
                        "type": "string",
                        "description": "Nombre del producto"
                    },
                    "cantidad": {
                        "type": "integer",
                        "description": "Cantidad a remover (null = todo)",
                        "nullable": True
                    }
                },
                "required": ["producto"]
            }
        ),
        mcp_types.Tool(
            name="vaciar_carrito",
            description="Vacía completamente el carrito",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        mcp_types.Tool(
            name="calcular_total",
            description="Calcula el total detallado del carrito",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        mcp_types.Tool(
            name="recomendar_productos",
            description="Recomienda productos por categoría o popularidad",
            inputSchema={
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": "string",
                        "description": "Categoría específica (opcional)",
                        "nullable": True
                    }
                }
            }
        ),
        mcp_types.Tool(
            name="mostrar_historial",
            description="Muestra el historial de búsquedas recientes",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    
    print(f"MCP Server: Advertising {len(tools)} tools")
    return tools

@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    """Execute a tool call requested by an MCP client."""
    print(f"MCP Server: Received call_tool request for '{name}' with args: {arguments}")
    
    try:
        result = None
        
        if name == "buscar_producto":
            # Search product
            nombre = arguments.get("nombre_producto", "")
            historial_busquedas.append(nombre)
            
            product_result = find_product_fuzzy(nombre)
            if product_result:
                key, producto = product_result
                result = {
                    "status": "success",
                    "product": serialize_product(producto),
                    "precio_formateado": format_price(producto.precio),
                    "disponible": producto.stock > 0,
                    "message": f"✅ Producto '{producto.nombre}' encontrado."
                }
            else:
                sugerencias = []
                for nombre_prod in list(PRODUCTOS_DB.keys())[:3]:
                    p = PRODUCTOS_DB[nombre_prod]
                    sugerencias.append(f"• {p.nombre} ({format_price(p.precio)})")
                
                result = {
                    "status": "not_found",
                    "message": f"❌ No encontré '{nombre}'.",
                    "sugerencias": sugerencias
                }
        
        elif name == "agregar_al_carrito":
            # Add to cart
            producto = arguments.get("producto", "")
            cantidad = arguments.get("cantidad", 1)
            
            if not isinstance(cantidad, int) or cantidad <= 0:
                result = {
                    "status": "error",
                    "message": "❌ La cantidad debe ser un número entero mayor que cero."
                }
            else:
                product_result = find_product_fuzzy(producto)
                if not product_result:
                    result = {
                        "status": "error",
                        "message": f"❌ No encontré el producto '{producto}'."
                    }
                else:
                    key, product_info = product_result
                    existing_item = get_cart_item_by_product(product_info.id)
                    cantidad_actual = existing_item.cantidad if existing_item else 0
                    
                    if cantidad_actual + cantidad > product_info.stock:
                        disponible = product_info.stock - cantidad_actual
                        result = {
                            "status": "error",
                            "message": f"❌ Stock insuficiente. Solo hay {disponible} unidades disponibles."
                        }
                    else:
                        if existing_item:
                            existing_item.cantidad += cantidad
                            existing_item.subtotal = existing_item.precio_unitario * existing_item.cantidad
                        else:
                            carrito.items.append(CartItem(
                                producto_id=product_info.id,
                                nombre=product_info.nombre,
                                precio_unitario=product_info.precio,
                                cantidad=cantidad
                            ))
                        
                        total_items = sum(item.cantidad for item in carrito.items)
                        subtotal = carrito.get_subtotal()
                        
                        result = {
                            "status": "success",
                            "message": f"✅ Agregado {cantidad}x '{product_info.nombre}' al carrito.",
                            "carrito_resumen": {
                                "total_items": total_items,
                                "subtotal": format_price(subtotal),
                                "envio_gratis": subtotal >= SHIPPING_THRESHOLD
                            }
                        }
        
        elif name == "ver_carrito":
            # View cart
            if not carrito.items:
                result = {
                    "status": "empty",
                    "message": "🛒 El carrito está vacío."
                }
            else:
                items_detail = []
                for item in carrito.items:
                    items_detail.append({
                        "nombre": item.nombre,
                        "cantidad": item.cantidad,
                        "precio_unitario": format_price(item.precio_unitario),
                        "subtotal": format_price(item.subtotal)
                    })
                
                subtotal = carrito.get_subtotal()
                discount = carrito.get_discount_amount()
                tax = carrito.get_tax()
                shipping = carrito.get_shipping()
                total = carrito.get_total()
                
                result = {
                    "status": "success",
                    "items": items_detail,
                    "calculos": {
                        "subtotal": format_price(subtotal),
                        "descuento": format_price(discount) if discount > 0 else None,
                        "codigo_descuento": carrito.discount_code,
                        "impuestos": format_price(tax),
                        "envio": format_price(shipping),
                        "total": format_price(total)
                    }
                }
        
        elif name == "aplicar_descuento":
            # Apply discount
            codigo = arguments.get("codigo", "").strip().upper()
            
            if not carrito.items:
                result = {
                    "status": "error",
                    "message": "❌ El carrito está vacío."
                }
            elif codigo not in DISCOUNT_CODES:
                result = {
                    "status": "error",
                    "message": f"❌ Código '{codigo}' no válido.",
                    "codigos_disponibles": list(DISCOUNT_CODES.keys())
                }
            else:
                carrito.discount_code = codigo
                descuento_pct = DISCOUNT_CODES[codigo]
                descuento_amt = carrito.get_discount_amount()
                
                result = {
                    "status": "success",
                    "message": f"✅ Código '{codigo}' aplicado: {int(descuento_pct * 100)}% de descuento",
                    "descuento": {
                        "porcentaje": f"{int(descuento_pct * 100)}%",
                        "monto": format_price(descuento_amt),
                        "total_con_descuento": format_price(carrito.get_total())
                    }
                }
        
        elif name == "remover_del_carrito":
            # Remove from cart
            producto = arguments.get("producto", "")
            cantidad = arguments.get("cantidad")
            
            product_result = find_product_fuzzy(producto)
            if not product_result:
                result = {
                    "status": "error",
                    "message": f"❌ Producto '{producto}' no encontrado."
                }
            else:
                key, product_info = product_result
                item = get_cart_item_by_product(product_info.id)
                
                if not item:
                    result = {
                        "status": "error",
                        "message": f"❌ '{product_info.nombre}' no está en el carrito."
                    }
                elif cantidad is None or cantidad >= item.cantidad:
                    carrito.items.remove(item)
                    result = {
                        "status": "success",
                        "message": f"✅ Removido '{product_info.nombre}' del carrito."
                    }
                elif cantidad > 0:
                    item.cantidad -= cantidad
                    item.subtotal = item.precio_unitario * item.cantidad
                    result = {
                        "status": "success",
                        "message": f"✅ Removidas {cantidad} unidades de '{product_info.nombre}'."
                    }
                else:
                    result = {
                        "status": "error",
                        "message": "❌ La cantidad debe ser mayor que cero."
                    }
        
        elif name == "vaciar_carrito":
            # Clear cart
            items_count = len(carrito.items)
            carrito.items.clear()
            carrito.discount_code = None
            
            result = {
                "status": "success",
                "message": "🧹 Carrito vaciado correctamente.",
                "productos_removidos": items_count
            }
        
        elif name == "calcular_total":
            # Calculate total
            if not carrito.items:
                result = {
                    "status": "empty",
                    "message": "El carrito está vacío.",
                    "total": format_price(0)
                }
            else:
                result = {
                    "status": "success",
                    "subtotal": format_price(carrito.get_subtotal()),
                    "descuento": format_price(carrito.get_discount_amount()),
                    "impuestos": format_price(carrito.get_tax()),
                    "envio": format_price(carrito.get_shipping()),
                    "total": format_price(carrito.get_total()),
                    "mensaje": f"💳 Total a pagar: {format_price(carrito.get_total())}"
                }
        
        elif name == "recomendar_productos":
            # Recommend products
            categoria = arguments.get("categoria")
            productos = list(PRODUCTOS_DB.values())
            
            if categoria:
                productos = [p for p in productos if p.categoria.lower() == categoria.lower()]
                if not productos:
                    result = {
                        "status": "error",
                        "message": f"No hay productos en la categoría '{categoria}'.",
                        "categorias_disponibles": list(set(p.categoria for p in PRODUCTOS_DB.values()))
                    }
                else:
                    productos.sort(key=lambda p: (p.rating, p.reviews), reverse=True)
                    recomendaciones = []
                    for p in productos[:3]:
                        recomendaciones.append({
                            "nombre": p.nombre,
                            "precio": format_price(p.precio),
                            "rating": f"⭐ {p.rating}/5.0",
                            "categoria": p.categoria
                        })
                    
                    result = {
                        "status": "success",
                        "categoria": categoria,
                        "recomendaciones": recomendaciones
                    }
            else:
                productos.sort(key=lambda p: (p.rating, p.reviews), reverse=True)
                recomendaciones = []
                for p in productos[:3]:
                    recomendaciones.append({
                        "nombre": p.nombre,
                        "precio": format_price(p.precio),
                        "rating": f"⭐ {p.rating}/5.0",
                        "categoria": p.categoria
                    })
                
                result = {
                    "status": "success",
                    "recomendaciones": recomendaciones
                }
        
        elif name == "mostrar_historial":
            # Show search history
            if not historial_busquedas:
                result = {
                    "status": "empty",
                    "message": "No hay búsquedas recientes."
                }
            else:
                result = {
                    "status": "success",
                    "historial": historial_busquedas[-5:],
                    "total_busquedas": len(historial_busquedas)
                }
        
        else:
            result = {
                "status": "error",
                "message": f"Tool '{name}' not implemented."
            }
        
        # Convert result to JSON string
        response_text = json.dumps(result, ensure_ascii=False, indent=2)
        return [mcp_types.TextContent(type="text", text=response_text)]
        
    except Exception as e:
        print(f"MCP Server: Error executing tool '{name}': {e}")
        error_text = json.dumps({
            "error": f"Failed to execute tool '{name}': {str(e)}"
        }, ensure_ascii=False)
        return [mcp_types.TextContent(type="text", text=error_text)]

# -------------------------
# MCP Server Runner
# -------------------------

async def run_mcp_stdio_server():
    """Runs the MCP server over standard input/output."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        print("MCP Stdio Server: Starting handshake with client...")
        
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
        print("MCP Stdio Server: Run loop finished or client disconnected.")

if __name__ == "__main__":
    print("Launching E-commerce MCP Server...")
    print("Available tools: buscar_producto, agregar_al_carrito, ver_carrito, etc.")
    print("Waiting for MCP client connections...")
    
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        print("\nMCP Server stopped by user.")
    except Exception as e:
        print(f"MCP Server encountered an error: {e}")
    finally:
        print("MCP Server process exiting.")