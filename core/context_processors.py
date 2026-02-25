"""
Context processors for making data available to all templates.
"""


def cart_context(request):
    """
    Add cart information to all template contexts.
    
    Provides:
    - cart_count: Total number of items in cart
    - cart_total_quantity: Sum of all product quantities
    
    Cart structure in session: {product_id: quantity}
    """
    cart = request.session.get('cart', {})
    
    # Calculate total number of items (sum of all quantities)
    cart_count = sum(cart.values()) if cart else 0
    
    return {
        'cart_count': cart_count,
        'cart': cart,
    }
