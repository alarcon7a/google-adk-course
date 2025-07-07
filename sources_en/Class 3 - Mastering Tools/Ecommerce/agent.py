"""
E-commerce Agent with Google ADK
A sophisticated e-commerce assistant using Google's Agent Development Kit.
"""

from google.adk.agents import Agent
from google.genai import types
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from difflib import get_close_matches
import json
import logging

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
    "mechanical rgb keyboard": Product(
        id="TEC005",
        name="Mechanical RGB Keyboard",
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
        description="4K gaming monitor with HDR for an immersive visual experience",
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
    "7.1 headphones": Product(
        id="AUR004",
        name="Gaming Headphones 7.1",
        price=150,
        stock=8,
        features=["7.1 Surround Sound", "Retractable microphone", "RGB", "Noise cancellation"],
        category="Audio",
        description="Gaming headphones with surround sound for maximum immersion",
        rating=4.5,
        reviews=94
    )
}

# -------------------------
# Shopping Cart State
# -------------------------

cart = Cart()
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
    for item in cart.items:
        if item.product_id == product_id:
            return item
    return None

# -------------------------
# Enhanced Tools
# -------------------------

def search_product_by_name(product_name: str) -> dict:
    """
    Search for a product by name with fuzzy search and record the search.
    
    Args:
        product_name: Name of the product to search for (flexible search).
        
    Returns:
        dict: Complete product details or suggestions if not found.
    """
    logger.info(f"🔍 Searching for product: '{product_name}'")
    search_history.append(product_name)
    
    result = find_product_fuzzy(product_name)
    
    if result:
        key, product = result
        return {
            "status": "success",
            "product": {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "formatted_price": format_price(product.price),
                "stock": product.stock,
                "features": product.features,
                "category": product.category,
                "description": product.description,
                "rating": f"⭐ {product.rating}/5.0 ({product.reviews} reviews)",
                "available": product.stock > 0
            },
            "message": f"✅ Product '{product.name}' found."
        }
    else:
        # Suggest similar products
        suggestions = []
        for name in list(PRODUCTS_DB.keys())[:3]:
            p = PRODUCTS_DB[name]
            suggestions.append(f"• {p.name} ({format_price(p.price)})")
        
        return {
            "status": "not_found",
            "message": f"❌ Couldn't find '{product_name}'.",
            "suggestions": suggestions,
            "suggestions_text": "Available products:\\n" + "\\n".join(suggestions)
        }

def add_to_cart(product: str, quantity: int = 1) -> dict:
    """
    Add products to cart with complete validation and intelligent search.
    
    Args:
        product: Product name (flexible search).
        quantity: Quantity to add (default: 1).
        
    Returns:
        dict: Confirmation with updated cart summary.
    """
    logger.info(f"🛒 Adding to cart: {quantity}x '{product}'")
    
    # Validate quantity
    if not isinstance(quantity, int) or quantity <= 0:
        return {
            "status": "error",
            "message": "❌ Quantity must be a positive integer."
        }
    
    # Find product
    result = find_product_fuzzy(product)
    if not result:
        return {
            "status": "error",
            "message": f"❌ Couldn't find product '{product}'. Use 'search_product' to see options."
        }
    
    key, product_info = result
    
    # Check if already in cart
    existing_item = get_cart_item_by_product(product_info.id)
    current_quantity = existing_item.quantity if existing_item else 0
    
    # Verify stock
    if current_quantity + quantity > product_info.stock:
        available = product_info.stock - current_quantity
        return {
            "status": "error",
            "message": f"❌ Insufficient stock. Only {available} units available for '{product_info.name}'.",
            "current_stock": product_info.stock,
            "in_cart": current_quantity,
            "available": available
        }
    
    # Add to cart
    if existing_item:
        existing_item.quantity += quantity
        existing_item.subtotal = existing_item.unit_price * existing_item.quantity
    else:
        cart.items.append(CartItem(
            product_id=product_info.id,
            name=product_info.name,
            unit_price=product_info.price,
            quantity=quantity
        ))
    
    total_items = sum(item.quantity for item in cart.items)
    subtotal = cart.get_subtotal()
    
    return {
        "status": "success",
        "message": f"✅ Added {quantity}x '{product_info.name}' to cart.",
        "added_product": {
            "name": product_info.name,
            "quantity": quantity,
            "unit_price": format_price(product_info.price),
            "subtotal": format_price(product_info.price * quantity)
        },
        "cart_summary": {
            "total_items": total_items,
            "subtotal": format_price(subtotal),
            "free_shipping": subtotal >= SHIPPING_THRESHOLD
        }
    }

def view_cart() -> dict:
    """
    Show detailed cart with subtotals, discounts and taxes.
    
    Returns:
        dict: Complete cart contents with calculations.
    """
    logger.info("👀 Showing cart")
    
    if not cart.items:
        return {
            "status": "empty",
            "message": "🛒 Cart is empty.",
            "suggestion": "You can search for available products or ask for recommendations."
        }
    
    # Build cart summary
    items_detail = []
    for item in cart.items:
        items_detail.append({
            "name": item.name,
            "quantity": item.quantity,
            "unit_price": format_price(item.unit_price),
            "subtotal": format_price(item.subtotal)
        })
    
    subtotal = cart.get_subtotal()
    discount = cart.get_discount_amount()
    tax = cart.get_tax()
    shipping = cart.get_shipping()
    total = cart.get_total()
    
    summary = {
        "status": "success",
        "items": items_detail,
        "total_products": len(cart.items),
        "total_units": sum(item.quantity for item in cart.items),
        "calculations": {
            "subtotal": format_price(subtotal),
            "discount": format_price(discount) if discount > 0 else None,
            "discount_code": cart.discount_code,
            "taxes": format_price(tax),
            "shipping": format_price(shipping),
            "free_shipping": shipping == 0,
            "total": format_price(total)
        }
    }
    
    # Add savings message if applicable
    if discount > 0:
        summary["savings_message"] = f"You're saving {format_price(discount)}!"
    if shipping == 0 and subtotal >= SHIPPING_THRESHOLD:
        summary["shipping_message"] = "Free shipping included!"
    
    return summary

def apply_discount(code: str) -> dict:
    """
    Apply a discount code to the cart.
    
    Args:
        code: Discount code to apply.
        
    Returns:
        dict: Confirmation with new total.
    """
    logger.info(f"🎟️ Applying discount code: {code}")
    
    if not cart.items:
        return {
            "status": "error",
            "message": "❌ Cart is empty. Add products before applying discounts."
        }
    
    code_upper = code.strip().upper()
    
    if code_upper not in DISCOUNT_CODES:
        return {
            "status": "error",
            "message": f"❌ Code '{code}' is not valid.",
            "available_codes": list(DISCOUNT_CODES.keys())
        }
    
    cart.discount_code = code_upper
    discount_pct = DISCOUNT_CODES[code_upper]
    discount_amt = cart.get_discount_amount()
    
    return {
        "status": "success",
        "message": f"✅ Code '{code_upper}' applied: {int(discount_pct * 100)}% discount",
        "discount": {
            "percentage": f"{int(discount_pct * 100)}%",
            "amount": format_price(discount_amt),
            "original_subtotal": format_price(cart.get_subtotal()),
            "total_with_discount": format_price(cart.get_total())
        }
    }

def remove_from_cart(product: str, quantity: Optional[int] = None) -> dict:
    """
    Remove products from cart (partially or completely).
    
    Args:
        product: Name of product to remove.
        quantity: Quantity to remove (None = remove all).
        
    Returns:
        dict: Operation confirmation.
    """
    logger.info(f"🗑️ Removing from cart: '{product}' (quantity: {quantity})")
    
    result = find_product_fuzzy(product)
    if not result:
        return {
            "status": "error",
            "message": f"❌ Product '{product}' not found in cart."
        }
    
    key, product_info = result
    item = get_cart_item_by_product(product_info.id)
    
    if not item:
        return {
            "status": "error",
            "message": f"❌ '{product_info.name}' is not in the cart."
        }
    
    if quantity is None or quantity >= item.quantity:
        # Remove completely
        cart.items.remove(item)
        return {
            "status": "success",
            "message": f"✅ Completely removed '{product_info.name}' from cart.",
            "removed_product": product_info.name,
            "removed_quantity": item.quantity
        }
    elif quantity > 0:
        # Remove partially
        item.quantity -= quantity
        item.subtotal = item.unit_price * item.quantity
        return {
            "status": "success",
            "message": f"✅ Removed {quantity} units of '{product_info.name}'.",
            "removed_quantity": quantity,
            "remaining_quantity": item.quantity
        }
    else:
        return {
            "status": "error",
            "message": "❌ Quantity must be greater than zero."
        }

def clear_cart() -> dict:
    """
    Completely empty the cart and reset discounts.
    
    Returns:
        dict: Operation confirmation.
    """
    logger.info("🧹 Clearing cart")
    
    items_count = len(cart.items)
    units_count = sum(item.quantity for item in cart.items)
    
    cart.items.clear()
    cart.discount_code = None
    
    return {
        "status": "success",
        "message": "🧹 Cart cleared successfully.",
        "removed_products": items_count,
        "removed_units": units_count
    }

def calculate_total() -> dict:
    """
    Calculate detailed cart total including all charges.
    
    Returns:
        dict: Complete cost breakdown.
    """
    logger.info("💰 Calculating cart total")
    
    if not cart.items:
        return {
            "status": "empty",
            "message": "Cart is empty.",
            "total": format_price(0)
        }
    
    subtotal = cart.get_subtotal()
    discount = cart.get_discount_amount()
    tax = cart.get_tax()
    shipping = cart.get_shipping()
    total = cart.get_total()
    
    # Build detailed breakdown
    breakdown = {
        "status": "success",
        "product_summary": [],
        "subtotal": format_price(subtotal),
        "discount": {
            "code": cart.discount_code,
            "amount": format_price(discount)
        } if discount > 0 else None,
        "taxes": {
            "rate": f"{int(TAX_RATE * 100)}%",
            "amount": format_price(tax)
        },
        "shipping": {
            "cost": format_price(shipping),
            "free": shipping == 0,
            "free_threshold": format_price(SHIPPING_THRESHOLD)
        },
        "total": format_price(total),
        "message": f"💳 Total to pay: {format_price(total)}"
    }
    
    # Add product details
    for item in cart.items:
        breakdown["product_summary"].append({
            "product": item.name,
            "quantity": item.quantity,
            "unit_price": format_price(item.unit_price),
            "subtotal": format_price(item.subtotal)
        })
    
    # Add savings information
    savings = []
    if discount > 0:
        savings.append(f"Discount: {format_price(discount)}")
    if shipping == 0 and subtotal >= SHIPPING_THRESHOLD:
        savings.append(f"Free shipping: {format_price(SHIPPING_COST)}")
    
    if savings:
        breakdown["total_savings"] = {
            "items": savings,
            "total": format_price(discount + (SHIPPING_COST if shipping == 0 else 0))
        }
    
    return breakdown

def recommend_products(category: Optional[str] = None) -> dict:
    """
    Recommend products based on category or popularity.
    
    Args:
        category: Specific category to filter (optional).
        
    Returns:
        dict: List of recommended products.
    """
    logger.info(f"🎯 Generating recommendations (category: {category})")
    
    products = list(PRODUCTS_DB.values())
    
    # Filter by category if specified
    if category:
        products = [p for p in products if p.category.lower() == category.lower()]
        if not products:
            return {
                "status": "error",
                "message": f"No products in category '{category}'.",
                "available_categories": list(set(p.category for p in PRODUCTS_DB.values()))
            }
    
    # Sort by rating and reviews
    products.sort(key=lambda p: (p.rating, p.reviews), reverse=True)
    
    recommendations = []
    for p in products[:3]:  # Top 3
        recommendations.append({
            "name": p.name,
            "price": format_price(p.price),
            "rating": f"⭐ {p.rating}/5.0",
            "category": p.category,
            "description": p.description,
            "available": p.stock > 0
        })
    
    return {
        "status": "success",
        "category": category or "All",
        "recommendations": recommendations,
        "message": f"🌟 Top {len(recommendations)} recommended products"
    }

def show_search_history() -> dict:
    """
    Show user's recent search history.
    
    Returns:
        dict: Search history.
    """
    if not search_history:
        return {
            "status": "empty",
            "message": "No recent searches."
        }
    
    return {
        "status": "success",
        "history": search_history[-5:],  # Last 5 searches
        "total_searches": len(search_history)
    }

# -------------------------
# Enhanced Agent Configuration
# -------------------------

root_agent = Agent(
    name="ecommerce_assistant_pro",
    model="gemini-2.5-flash",
    description="Advanced e-commerce assistant with intelligent search, cart management and personalized recommendations.",
    instruction=(
        "You are a professional and friendly shopping assistant. Your goal is to help users:\\n"
        "1. Find products using flexible search (they don't need to write the exact name)\\n"
        "2. Manage their shopping cart efficiently\\n"
        "3. Apply discounts and calculate totals with taxes and shipping\\n"
        "4. Receive personalized recommendations\\n\\n"
        "Special features:\\n"
        "- Intelligent search: finds products even if the name isn't exact\\n"
        "- Automatic calculation of taxes (8%) and shipping (free over $100)\\n"
        "- Discount codes: WELCOME10 (10%), SAVE20 (20%), VIP30 (30%)\\n"
        "- Recommendations based on popularity and category\\n\\n"
        "Be proactive:\\n"
        "- If you can't find a product, suggest similar alternatives\\n"
        "- Mention when the user is close to free shipping\\n"
        "- Remember to inform about available discounts\\n"
        "- Highlight product features and ratings"
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=800,
        top_p=0.9
    ),
    tools=[
        search_product_by_name,
        add_to_cart,
        view_cart,
        apply_discount,
        remove_from_cart,
        clear_cart,
        calculate_total,
        recommend_products,
        show_search_history
    ],
)