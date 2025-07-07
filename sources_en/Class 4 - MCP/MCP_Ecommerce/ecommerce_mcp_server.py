# ecommerce_mcp_server.py
"""
MCP server that exposes e-commerce functions through the Model Context Protocol.
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
    name: str
    price: float
    stock: int
    features: List[str]
    category: str = "General"
    description: str = ""
    rating: float = 0.0
    reviews: int = 0

@dataclass
class CartItem:
    """Cart item model."""
    product_id: str
    name: str
    unit_price: float
    quantity: int
    subtotal: float = field(init=False)
    
    def __post_init__(self):
        self.subtotal = self.unit_price * self.quantity

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

PRODUCTS_DB: Dict[str, Product] = {
    "gaming laptop pro": Product(
        id="LPG001",
        name="Gaming Laptop Pro",
        price=1500,
        stock=10,
        features=["RTX 4070", "32GB RAM", "1TB SSD", "144Hz Display"],
        category="Computers",
        description="High-end gaming laptop for the most demanding games",
        rating=4.8,
        reviews=127
    ),
    "mechanical keyboard rgb": Product(
        id="TEC005",
        name="Mechanical Keyboard RGB",
        price=120,
        stock=25,
        features=["Cherry MX Switches", "Customizable RGB", "TKL", "USB-C"],
        category="Peripherals",
        description="Premium mechanical keyboard with full RGB lighting",
        rating=4.6,
        reviews=89
    ),
    "4k hdr monitor": Product(
        id="MON003",
        name="4K HDR Monitor",
        price=400,
        stock=5,
        features=["27 inches", "144Hz", "HDR10", "G-Sync Compatible"],
        category="Monitors",
        description="4K gaming monitor with HDR for immersive visual experience",
        rating=4.9,
        reviews=203
    ),
    "gaming mouse pro": Product(
        id="MOU002",
        name="Gaming Mouse Pro",
        price=80,
        stock=15,
        features=["16000 DPI", "RGB", "8 programmable buttons", "Wireless"],
        category="Peripherals",
        description="Professional gaming mouse with high-precision sensor",
        rating=4.7,
        reviews=156
    ),
    "gaming headset 7.1": Product(
        id="AUR004",
        name="Gaming Headset 7.1",
        price=150,
        stock=8,
        features=["7.1 Surround Sound", "Retractable Microphone", "RGB", "Noise Cancellation"],
        category="Audio",
        description="Gaming headset with surround sound for maximum immersion",
        rating=4.5,
        reviews=94
    )
}

# -------------------------
# Shopping Cart State
# -------------------------

shopping_cart = Cart()
search_history: List[str] = []

# -------------------------
# Helper Functions
# -------------------------

def find_product_fuzzy(name: str) -> Optional[Tuple[str, Product]]:
    """Find product using fuzzy matching."""
    name_lower = name.strip().lower()
    
    # Exact match
    if name_lower in PRODUCTS_DB:
        return name_lower, PRODUCTS_DB[name_lower]
    
    # Fuzzy match
    product_names = list(PRODUCTS_DB.keys())
    matches = get_close_matches(name_lower, product_names, n=1, cutoff=0.6)
    
    if matches:
        match = matches[0]
        return match, PRODUCTS_DB[match]
    
    return None

def format_price(amount: float) -> str:
    """Format price with currency."""
    return f"${amount:,.2f}"

def get_cart_item_by_product(product_id: str) -> Optional[CartItem]:
    """Get cart item by product ID."""
    for item in shopping_cart.items:
        if item.product_id == product_id:
            return item
    return None

def serialize_cart_item(item: CartItem) -> dict:
    """Serialize CartItem to dict."""
    return {
        "product_id": item.product_id,
        "name": item.name,
        "unit_price": item.unit_price,
        "quantity": item.quantity,
        "subtotal": item.subtotal
    }

def serialize_product(product: Product) -> dict:
    """Serialize Product to dict."""
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
        "features": product.features,
        "category": product.category,
        "description": product.description,
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
            name="search_product",
            description="Search for a product by name with fuzzy search",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Name of the product to search for"
                    }
                },
                "required": ["product_name"]
            }
        ),
        mcp_types.Tool(
            name="add_to_cart",
            description="Add products to cart with stock validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Product name"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity to add",
                        "default": 1
                    }
                },
                "required": ["product"]
            }
        ),
        mcp_types.Tool(
            name="view_cart",
            description="Show detailed cart with calculations",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        mcp_types.Tool(
            name="apply_discount",
            description="Apply a discount code to the cart",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Discount code"
                    }
                },
                "required": ["code"]
            }
        ),
        mcp_types.Tool(
            name="remove_from_cart",
            description="Remove products from cart",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Product name"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity to remove (null = all)",
                        "nullable": True
                    }
                },
                "required": ["product"]
            }
        ),
        mcp_types.Tool(
            name="clear_cart",
            description="Clear the entire cart",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        mcp_types.Tool(
            name="calculate_total",
            description="Calculate detailed cart total",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        mcp_types.Tool(
            name="recommend_products",
            description="Recommend products by category or popularity",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Specific category (optional)",
                        "nullable": True
                    }
                }
            }
        ),
        mcp_types.Tool(
            name="show_history",
            description="Show recent search history",
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
        
        if name == "search_product":
            # Search product
            product_name = arguments.get("product_name", "")
            search_history.append(product_name)
            
            product_result = find_product_fuzzy(product_name)
            if product_result:
                key, product = product_result
                result = {
                    "status": "success",
                    "product": serialize_product(product),
                    "formatted_price": format_price(product.price),
                    "available": product.stock > 0,
                    "message": f"✅ Product '{product.name}' found."
                }
            else:
                suggestions = []
                for prod_name in list(PRODUCTS_DB.keys())[:3]:
                    p = PRODUCTS_DB[prod_name]
                    suggestions.append(f"• {p.name} ({format_price(p.price)})")
                
                result = {
                    "status": "not_found",
                    "message": f"❌ Couldn't find '{product_name}'.",
                    "suggestions": suggestions
                }
        
        elif name == "add_to_cart":
            # Add to cart
            product = arguments.get("product", "")
            quantity = arguments.get("quantity", 1)
            
            if not isinstance(quantity, int) or quantity <= 0:
                result = {
                    "status": "error",
                    "message": "❌ Quantity must be a positive integer."
                }
            else:
                product_result = find_product_fuzzy(product)
                if not product_result:
                    result = {
                        "status": "error",
                        "message": f"❌ Couldn't find product '{product}'."
                    }
                else:
                    key, product_info = product_result
                    existing_item = get_cart_item_by_product(product_info.id)
                    current_quantity = existing_item.quantity if existing_item else 0
                    
                    if current_quantity + quantity > product_info.stock:
                        available = product_info.stock - current_quantity
                        result = {
                            "status": "error",
                            "message": f"❌ Insufficient stock. Only {available} units available."
                        }
                    else:
                        if existing_item:
                            existing_item.quantity += quantity
                            existing_item.subtotal = existing_item.unit_price * existing_item.quantity
                        else:
                            shopping_cart.items.append(CartItem(
                                product_id=product_info.id,
                                name=product_info.name,
                                unit_price=product_info.price,
                                quantity=quantity
                            ))
                        
                        total_items = sum(item.quantity for item in shopping_cart.items)
                        subtotal = shopping_cart.get_subtotal()
                        
                        result = {
                            "status": "success",
                            "message": f"✅ Added {quantity}x '{product_info.name}' to cart.",
                            "cart_summary": {
                                "total_items": total_items,
                                "subtotal": format_price(subtotal),
                                "free_shipping": subtotal >= SHIPPING_THRESHOLD
                            }
                        }
        
        elif name == "view_cart":
            # View cart
            if not shopping_cart.items:
                result = {
                    "status": "empty",
                    "message": "🛒 Cart is empty."
                }
            else:
                items_detail = []
                for item in shopping_cart.items:
                    items_detail.append({
                        "name": item.name,
                        "quantity": item.quantity,
                        "unit_price": format_price(item.unit_price),
                        "subtotal": format_price(item.subtotal)
                    })
                
                subtotal = shopping_cart.get_subtotal()
                discount = shopping_cart.get_discount_amount()
                tax = shopping_cart.get_tax()
                shipping = shopping_cart.get_shipping()
                total = shopping_cart.get_total()
                
                result = {
                    "status": "success",
                    "items": items_detail,
                    "calculations": {
                        "subtotal": format_price(subtotal),
                        "discount": format_price(discount) if discount > 0 else None,
                        "discount_code": shopping_cart.discount_code,
                        "tax": format_price(tax),
                        "shipping": format_price(shipping),
                        "total": format_price(total)
                    }
                }
        
        elif name == "apply_discount":
            # Apply discount
            code = arguments.get("code", "").strip().upper()
            
            if not shopping_cart.items:
                result = {
                    "status": "error",
                    "message": "❌ Cart is empty."
                }
            elif code not in DISCOUNT_CODES:
                result = {
                    "status": "error",
                    "message": f"❌ Code '{code}' is not valid.",
                    "available_codes": list(DISCOUNT_CODES.keys())
                }
            else:
                shopping_cart.discount_code = code
                discount_pct = DISCOUNT_CODES[code]
                discount_amt = shopping_cart.get_discount_amount()
                
                result = {
                    "status": "success",
                    "message": f"✅ Code '{code}' applied: {int(discount_pct * 100)}% discount",
                    "discount": {
                        "percentage": f"{int(discount_pct * 100)}%",
                        "amount": format_price(discount_amt),
                        "total_with_discount": format_price(shopping_cart.get_total())
                    }
                }
        
        elif name == "remove_from_cart":
            # Remove from cart
            product = arguments.get("product", "")
            quantity = arguments.get("quantity")
            
            product_result = find_product_fuzzy(product)
            if not product_result:
                result = {
                    "status": "error",
                    "message": f"❌ Product '{product}' not found."
                }
            else:
                key, product_info = product_result
                item = get_cart_item_by_product(product_info.id)
                
                if not item:
                    result = {
                        "status": "error",
                        "message": f"❌ '{product_info.name}' is not in cart."
                    }
                elif quantity is None or quantity >= item.quantity:
                    shopping_cart.items.remove(item)
                    result = {
                        "status": "success",
                        "message": f"✅ Removed '{product_info.name}' from cart."
                    }
                elif quantity > 0:
                    item.quantity -= quantity
                    item.subtotal = item.unit_price * item.quantity
                    result = {
                        "status": "success",
                        "message": f"✅ Removed {quantity} units of '{product_info.name}'."
                    }
                else:
                    result = {
                        "status": "error",
                        "message": "❌ Quantity must be greater than zero."
                    }
        
        elif name == "clear_cart":
            # Clear cart
            items_count = len(shopping_cart.items)
            shopping_cart.items.clear()
            shopping_cart.discount_code = None
            
            result = {
                "status": "success",
                "message": "🧹 Cart cleared successfully.",
                "products_removed": items_count
            }
        
        elif name == "calculate_total":
            # Calculate total
            if not shopping_cart.items:
                result = {
                    "status": "empty",
                    "message": "Cart is empty.",
                    "total": format_price(0)
                }
            else:
                result = {
                    "status": "success",
                    "subtotal": format_price(shopping_cart.get_subtotal()),
                    "discount": format_price(shopping_cart.get_discount_amount()),
                    "tax": format_price(shopping_cart.get_tax()),
                    "shipping": format_price(shopping_cart.get_shipping()),
                    "total": format_price(shopping_cart.get_total()),
                    "message": f"💳 Total to pay: {format_price(shopping_cart.get_total())}"
                }
        
        elif name == "recommend_products":
            # Recommend products
            category = arguments.get("category")
            products = list(PRODUCTS_DB.values())
            
            if category:
                products = [p for p in products if p.category.lower() == category.lower()]
                if not products:
                    result = {
                        "status": "error",
                        "message": f"No products in category '{category}'.",
                        "available_categories": list(set(p.category for p in PRODUCTS_DB.values()))
                    }
                else:
                    products.sort(key=lambda p: (p.rating, p.reviews), reverse=True)
                    recommendations = []
                    for p in products[:3]:
                        recommendations.append({
                            "name": p.name,
                            "price": format_price(p.price),
                            "rating": f"⭐ {p.rating}/5.0",
                            "category": p.category
                        })
                    
                    result = {
                        "status": "success",
                        "category": category,
                        "recommendations": recommendations
                    }
            else:
                products.sort(key=lambda p: (p.rating, p.reviews), reverse=True)
                recommendations = []
                for p in products[:3]:
                    recommendations.append({
                        "name": p.name,
                        "price": format_price(p.price),
                        "rating": f"⭐ {p.rating}/5.0",
                        "category": p.category
                    })
                
                result = {
                    "status": "success",
                    "recommendations": recommendations
                }
        
        elif name == "show_history":
            # Show search history
            if not search_history:
                result = {
                    "status": "empty",
                    "message": "No recent searches."
                }
            else:
                result = {
                    "status": "success",
                    "history": search_history[-5:],
                    "total_searches": len(search_history)
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
    print("Available tools: search_product, add_to_cart, view_cart, etc.")
    print("Waiting for MCP client connections...")
    
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        print("\nMCP Server stopped by user.")
    except Exception as e:
        print(f"MCP Server encountered an error: {e}")
    finally:
        print("MCP Server process exiting.")